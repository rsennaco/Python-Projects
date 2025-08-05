# Auditing AWS Security Groups

---

### The Problem

I was tasked with figuring out the use case for a number of security groups in our AWS environment that had a description missing.

I think I was given like....200 something security groups with each SGR pushed out to a seperate line. I think this ended up being a 700 row excel document.

I was trying to figure out how to quickly dig through the rules and find out a generalized use case based on the ports given, and ended up working out the two above python scripts to do this.

### The Solution

I grabbed all of the SG IDs and saved them to a file called sg_ids, used this list as an input for `gather_sg_details.py` which creates 2 files; `sg_details.json` and `sg_does_not_exist.json`.

So we get a fatty json that has all the relevant information I need about the SGs and a dump list of SGs in the original excel document that aren't actually in the AWS environment.

The script uses the local .aws/credentials file to connect with the AWS resources. Thankfully this was only within one of our AWS accounts, the script doesn't attempt to make connections to multiple AWS accounts.

The second script `export_to_excel.py` reads from the `sg_details.json` file, builds a useCase string based on port information and details from things like the SG name or description and creates a new excel file named whatever you put in for the `$2` argument

This gave me a 98% way there product that I had to tweak just a bit but was purrrrty good! Try it out if you'd like!
