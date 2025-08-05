import boto3
import json
import sys
from botocore.exceptions import ClientError

def read_sg_ids_from_file(filename):
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip()]

def get_security_group_details(sg_ids, output_file='sg_details.json', not_found_file='sg_does_not_exist.json'):
    ec2 = boto3.client('ec2')
    sg_details = []
    not_found_sgs = []

    for sg_id in sg_ids:
        try:
            response = ec2.describe_security_groups(GroupIds=[sg_id])
            for sg in response['SecurityGroups']:
                sg_name = sg.get('GroupName', '')
                sg_desc = sg.get('Description', '')
                
                eni_response = ec2.describe_network_interfaces(
                    Filters=[
                        {'Name': 'group-id', 'Values': [sg_id]}
                    ]
                )

                assigned_devices = []
                instance_ids = [eni['Attachment']['InstanceId'] for eni in eni_response['NetworkInterfaces']
                    if eni.get('Attachment') and eni['Attachment'].get('InstanceId')]

                instance_name_map = {}
                if instance_ids:
                    instances = ec2.describe_instances(InstanceIds=instance_ids)
                    for reservation in instances['Reservations']:
                        for instance in reservation['Instances']:
                            name = ""
                            for tag in instance.get('Tags', []):
                                if tag['Key'] == 'Name':
                                    name = tag['Value']
                                    break
                            instance_name_map[instance['InstanceId']] = name

                for eni in eni_response['NetworkInterfaces']:
                    instance_id = None
                    instance_name = None
                    if eni.get('Attachment') and eni['Attachment'].get('InstanceId'):
                        instance_id = eni['Attachment']['InstanceId']
                        instance_name = instance_name_map.get(instance_id)
                    assigned_devices.append({
                        'NetworkInterfaceId': eni['NetworkInterfaceId'],
                        'InstanceId': instance_id,
                        'InstanceName': instance_name
                    })

                sg_rules = []
                for perm in sg.get('IpPermissions', []):
                    port = perm.get('FromPort', 'All') if 'FromPort' in perm else 'All'
                    protocol = perm.get('IpProtocol', 'All')
                    for ip_range in perm.get('IpRanges', []):
                        rule_name = ip_range.get('Description', '')
                        source_cidr = ip_range.get('CidrIp', '')
                        rule_desc = ip_range.get('Description', '')
                        sg_rules.append({
                            'Name': rule_name,
                            'Port': port,
                            'Protocol': protocol,
                            'SourceCIDR': source_cidr,
                            'Description': rule_desc
                        })
                    for ipv6_range in perm.get('Ipv6Ranges', []):
                        rule_name = ipv6_range.get('Description', '')
                        source_cidr = ipv6_range.get('CidrIpv6', '')
                        rule_desc = ipv6_range.get('Description', '')
                        sg_rules.append({
                            'Name': rule_name,
                            'Port': port,
                            'Protocol': protocol,
                            'SourceCIDR': source_cidr,
                            'Description': rule_desc
                        })

                sg_details.append({
                    'SecurityGroupId': sg_id,
                    'Name': sg_name,
                    'Description': sg_desc,
                    'AssignedDevices': assigned_devices,
                    'Rules': sg_rules
                })
        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidGroup.NotFound':
                not_found_sgs.append(sg_id)
                print(f"Security group does not exist: {sg_id}")
            else:
                print(f"Error fetching details for {sg_id}: {e}")

    with open(output_file, 'w') as f:
        json.dump(sg_details, f, indent=4)
    print(f"Security group details saved to {output_file}")

    if not_found_sgs:
        with open(not_found_file, 'w') as nf:
            json.dump(not_found_sgs, nf, indent=4)
        print(f"Non-existent security groups saved to {not_found_file}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python gather_sg_details.py <sg_ids_file> [output_json_file]")
        sys.exit(1)

    sg_ids_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "sg_details.json"
    not_found_file = "sg_does_not_exist.json"

    sg_ids = read_sg_ids_from_file(sg_ids_file)
    get_security_group_details(sg_ids, output_file, not_found_file)
