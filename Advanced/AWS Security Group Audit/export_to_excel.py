import json
import pandas as pd
import argparse
import re
import openpyxl

def oxford_comma(items):
    items = list(items)
    if not items:
        return ''
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])}, and {items[-1]}"

# this builds out some attributes for team name, environment, and application
# based on our naming conventions
def extract_details(instance_name):
    if instance_name and isinstance(instance_name, str) and instance_name.startswith('project-'):
        parts = instance_name.split('-')
        if len(parts) >= 4:
            team = parts[1]
            environment = parts[2]
            application = '-'.join(parts[3:])
            return team, environment, application
    if instance_name and isinstance(instance_name, str) and ('karpenter-node' in instance_name or 'standard-node' in instance_name):
        parts = instance_name.split('-')
        if len(parts) >= 3:
            environment = parts[1]
            return None, environment, "EKS Nodes"
    return None, None, None

# This bit pulls out some information for sagemaker domains
# based on our naming conventions
def extract_sagemaker_domain_info(sg_name):
    pattern1 = r"ai-d-(?P<domainid>[a-zA-Z0-9]+)-(?P<firstname>[a-zA-Z]+)-(?P<lastname>[a-zA-Z]+)"
    match = re.match(pattern1, sg_name)
    if match:
        domainid = match.group("domainid")
        firstname = match.group("firstname").capitalize()
        lastname = match.group("lastname").capitalize()
        return ("user", firstname, lastname, domainid)

# This tries to pull some tenant name if nothing else works
def try_extract_team_from_description(desc):
    if not desc or not isinstance(desc, str):
        return None
    match = re.search(r"(?:for|by)\s+([a-zA-Z0-9_-]+)", desc)
    if match:
        return match.group(1)
    match = re.search(r"Allows\s+([a-zA-Z0-9_-]+)", desc)
    if match:
        return match.group(1)
    return None

def check_bastion_host(sg_name):
    if sg_name and isinstance(sg_name, str) and "bastion" in sg_name.lower():
        return "Bastion Host"
    return None

def check_kubernetes_elb(desc):
    if desc and isinstance(desc, str) and 'kubernetes elb' in desc.lower():
        return 'EKS ELB'
    return None

def assigned_status(assigned_devices):
    if not assigned_devices:
        return "No"
    has_ec2 = any(
        d.get('InstanceId') not in [None, "null"] or d.get('InstanceName') not in [None, "null"]
        for d in assigned_devices
    )
    if has_ec2:
        return "Yes"
    return "Yes (ENI Only)"

def parse_security_groups(json_path):
    with open(json_path) as f:
        data = json.load(f)

    rows = []
    for sg in data:
        sg_id = sg.get('SecurityGroupId', '')
        name = sg.get('Name', '')
        desc = sg.get('Description', '')
        assigned_devices = sg.get('AssignedDevices', [])
        rules = sg.get('Rules', [])
        base_use_case = infer_use_cases(rules, name, desc)
        sagemaker_type, firstname, lastname, domainid = extract_sagemaker_domain_info(name)
        
        devices_set = {d.get('InstanceName') for d in assigned_devices if d.get('InstanceName')}
        devices_str = ','.join(sorted(devices_set))

        rules_summary = set()
        for rule in rules:
            p = rule.get('Port', '')
            proto = rule.get('Protocol', '')
            rules_summary.add(f"{proto}/{p}")
        rules_str = ','.join(sorted(rules_summary))

        teams, environments, applications = set(), set(), set()
        for device in assigned_devices:
            instance_name = device.get('InstanceName')
            team, environment, application = extract_details(instance_name)
            if team:
                teams.add(team)
            if environment:
                environments.add(environment)
            if application:
                applications.add(application)

        team_str = oxford_comma(sorted(teams)) if teams else ''
        env_str = oxford_comma(sorted(environments)) if environments else ''
        app_str = oxford_comma(sorted(applications)) if applications else ''

        use_case_set = infer_use_cases(rules, name, desc)
        use_case_list = sorted(use_case_set)
        use_case_text = f"{oxford_comma(use_case_list)} Access"
        
        elb = check_kubernetes_elb(desc)
        bastion_host = check_bastion_host(name)

        if elb:
            team_str = elb
            env_str = ""
            app_str = ""
        if bastion_host:
            team_str = bastion_host
            env_str = ""
            app_str = ""

        if base_use_case == "unknown":
            use_case_final = "unknown"

        if sagemaker_type == "user" and firstname and lastname and domainid:
            use_case_final = f"{use_case_text} for SageMaker Domain d-{domainid}: {firstname} {lastname}"
        elif sagemaker_type == "nfs" and not firstname and not lastname and domainid:
            use_case_final = f"Inbound NFS Traffic for SageMaker Domain d-{domainid}"
        else:
            use_case_final = use_case_text
            if team_str:
                use_case_final += f" for {team_str}"
            if env_str:
                use_case_final += f" in {env_str}"
            if app_str:
                use_case_final += f" for {app_str}"

        rows.append({
            'SecurityGroupID': sg_id,
            'Name': name,
            'Assigned': assigned_status(assigned_devices),
            'UseCase': use_case_final,
            'Rules': rules_str,
            'Description': desc,
            'AssignedDevices': devices_str,
        })

    return pd.DataFrame(rows)

# This is probably a dumb way to do this
# maybe a map is more effective, but this also worked
def infer_use_cases(rules, sg_name="", sg_description=""):
    if not rules:
        return {"unknown"}
    use_cases = set()
    for r in rules:
        port = r.get('Port')
        proto = r.get('Protocol')
        uc = None
        if port == -1 and proto == 'icmp':
            uc = 'All ICMP Traffic within VPC'
        elif port == 0 and proto == 'tcp':
            uc = 'All TCP Traffic within VPC'
        elif port == 3 and proto == 'icmp':
            uc = 'ICMP Destination Unreachable'
        elif port == 8 and proto == 'icmp':
            uc = 'ICMP Echo Request'
        elif port == 22:
            uc = 'SSH'
        elif port == 53 and proto == 'udp':
            uc = 'DNS'
        elif port == 80:
            uc = 'HTTP'
        elif port == 443:
            uc = 'HTTPS'
        elif port == 123:
            uc = 'NTP'
        elif port == 161:
            uc = 'ScienceLogic SNMP'
        elif port in [88, 389, 464, 636, 749, 789]:
            uc = 'LDAP/Kerberos'
        elif port == 988:
            uc = 'NFS Luster Data'
        
        #Additional port mappings hidden

        if uc and uc != 'unknown':
            use_cases.add(uc)
    return use_cases or {'unknown'}

def main():
    parser = argparse.ArgumentParser(description='Export security group use cases to Excel.')
    parser.add_argument('--input', '-i', required=True, help='Path to input JSON file')
    parser.add_argument('--output', '-o', required=True, help='Path to output Excel file')
    args = parser.parse_args()

    df = parse_security_groups(args.input)
    df.to_excel(args.output, index=False)

    print(f"Exported {len(df)} security groups to {args.output}")

if __name__ == '__main__':
    main()
