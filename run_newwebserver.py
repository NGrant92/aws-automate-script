#!/usr/bin/env python3

import boto3
import time
import subprocess
import os
from utils import input_int
from utils import clear
from utils import add_header
from utils import return_menu

# Declaring ec2 and s3 variable
ec2 = boto3.resource('ec2')
s3 = boto3.resource('s3')
key_dir = "~/comp_sci/dev-ops/lab00key.pem"


# To create an instance and add a tag to it after creation
def create_instance():
    add_header("Creating Instance")
    key = "lab00key"
    key_dir = "~/comp_sci/dev-ops/lab00key.pem"
    # string to hold instance name
    value = 'instance name here'
    # Holds tag info
    tags = [{'Key': 'Name', 'Value': value}]
    # Used for TagSpecification field to name the instance
    tag_spec = [{'ResourceType': 'instance', 'Tags': tags}]

    # A try/except to prevent the script from crashing
    try:
        # creation of instance
        instance = ec2.create_instances(
            ImageId='ami-acd005d5',
            MinCount=1,
            MaxCount=1,
            SecurityGroupIds=['sg-872f06ff'],
            KeyName=key,
            TagSpecifications=tag_spec,
            UserData='''#!/bin/bash
                yum -y update
                yum -y install nginx
                yum -y install python35
                service nginx start
                chkconfig nginx on
                touch home/ec2-user/testFile''',
            InstanceType='t2.micro')
        
        print("Created an instance with ID:", instance[0].id)
        time.sleep(5)
        instance[0].reload()
        inst_ip = instance[0].public_ip_address
        print("Public IP address:", inst_ip)
        
        # ssh_cmd = "ssh -i %s ec2-user@%s '%s'"
        
        cmd = "ssh -o StrictHostKeyChecking=no -i" + key_dir + " ec2-user@" + inst_ip + " 'pwd'"
        time.sleep(40)
        (status, output) = subprocess.getstatusoutput(cmd)
        print(output)

        scp_cmd = "scp -i " + key_dir + " check_webserver.py ec2-user@" + inst_ip + ":."
        (status, output) = subprocess.getstatusoutput(scp_cmd)
        if status > 0:
            print("check_webserver.py was not added to instance")
        else:
            print("Copied check_webserver.py to instance")
        
        return inst_ip
        
    except Exception as error:
        print(error)
    

# Function to run the check_webserver.py file that's stored in the EC2 instance
def run_check_webserver(key_dir, inst_ip):
    add_header("Checking Webserver")
    run_check = 'ssh -i ' + key_dir + ' ec2-user@' + inst_ip + ' python3 check_webserver.py'
    os.system(run_check)

    
# Function to create a new bucket
def new_bucket():
    add_header("Creating Bucket")
    is_unique = False
    # a while loop incase the user's bucket name in already taken or incorrect syntax
    while not is_unique:
        
        # asks for user to input bucket name
        print("\nBack to menu type: ex")
        be_name = input("Enter Bucket name: ")
        # if user types "ex" it'll exit out of the create_bucket() function
        if be_name == "ex":
            print("\nReturning to menu...")
            time.sleep(3)
            return
            
        # A try/except to prevent the script from crashing
        try:
            # Creates a bucket and setting its location to the Ireland servers
            response = s3.create_bucket(Bucket=be_name, CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
            # prints out its result to console for user
            print("\nBucket successfully created!")
            print(response)
            is_unique = True
        except Exception as error:
            # prints out error to console for user
            print("ERROR: \n" + str(error))


# To upload an object to a specified bucket
def put_bucket(bucket, file):
    add_header("Uploading file to bucket")
    if not bucket and not file:
        print("No bucket or file")

    # A try/except to prevent the script from crashing
    try:
        # uploading file to the specified bucket
        response = s3.Object(bucket, file).put(Body=open(file, 'rb'))
        # prints out its result to console for user
        print(response)
    except Exception as error:
        # prints out error to console for user
        print(error)


def list_buckets():
    bucket_list = []
    
    for inst in ec2.instances.all():
        if inst.state['Name'] == "running":
            inst_tup = (inst.tags[0]['Value'], inst.id, inst.public_ip_address, inst.state['Name'])
            bucket_list.append(inst_tup)
        else:
            inst_tup = (inst.tags[0]['Value'], inst.id, "", inst.state['Name'])
            bucket_list.append(inst_tup)
    
    if len(bucket_list) == 1:
        return bucket_list[0]
    
    elif len(bucket_list) > 1:
        max_w = 111
        w = 25
        
        title = "|%s|" % "Instance List".center(max_w)
        dec = "+%s+" % ("-"*max_w)
        col_names = "|%s|%s|%s|%s|%s|" % ("#".center(7), "Name".center(w), "ID".center(w), "Public IP".center(w), "State".center(w))
        
        list_str = ""
        for inst in bucket_list:
            index = str(bucket_list.index(inst))
            line = "|%s|%s|%s|%s|%s|" % (index.center(7), inst[0].center(w), inst[1].center(w), inst[2].center(w), inst[3].center(w))
            list_str += "\n" + line
        
        print(dec + "\n" + title + "\n" + dec + "\n" + col_names + "\n" + dec + list_str + "\n" + dec)
        i = int(input_int("Select instance number(#):\n> "))
        return bucket_list[i]
    else:
        print("No instances detected!")


def list_instances():
    inst_list = []
    
    for inst in ec2.instances.all():
        if inst.state['Name'] == "running":
            inst_tup = (inst.tags[0]['Value'], inst.id, inst.public_ip_address, inst.state['Name'])
            inst_list.append(inst_tup)
        else:
            inst_tup = (inst.tags[0]['Value'], inst.id, "", inst.state['Name'])
            inst_list.append(inst_tup)
    
    if len(inst_list) == 1:
        return inst_list[0]
    
    elif len(inst_list) > 1:
        max_w = 111
        w = 25
        
        title = "|%s|" % "Instance List".center(max_w)
        dec = "+%s+" % ("-"*max_w)
        col_names = "|%s|%s|%s|%s|%s|" % ("#".center(7), "Name".center(w), "ID".center(w), "Public IP".center(w), "State".center(w))
        
        list_str = ""
        for inst in inst_list:
            index = str(inst_list.index(inst))
            line = "|%s|%s|%s|%s|%s|" % (index.center(7), inst[0].center(w), inst[1].center(w), inst[2].center(w), inst[3].center(w))
            list_str += "\n" + line
        
        print(dec + "\n" + title + "\n" + dec + "\n" + col_names + "\n" + dec + list_str + "\n" + dec)
        i = int(input_int("Select instance number(#):\n> "))
        return inst_list[i]
    else:
        print("No instances detected!")


# Creates new instance, copies check_webserver.py to instance and runs it remotely
# function is created to avoid duplication as code is used in menu option 1 & 4
def new_instance():
    clear()
    # function creates a new instance and returns the public IP
    inst_ip = create_instance()
    time.sleep(15)
    # .py file that is copied to instance is run remotely through ssh
    run_check_webserver(key_dir, inst_ip)


def main():

    key_dir = "~/comp_sci/dev-ops/lab00key.pem"
    while True:
        menu = open('menu.txt', 'rU')
        print(menu.read())
        menu_in = input_int("> ")
    
        # Option 1: To create an instance and bucket
        # When instance is made, check_webserver.py is added and run
        if menu_in == "1":
            # create_instance() and run_check_webserver() functions
            new_instance()
            time.sleep(5)
            # function creates new bucket
            new_bucket()
            return_menu()
        
        # Option 2: It will display a list of user's instances (if more than 1)
        # User will select an instance and run_check_webserver() will be called
        elif menu_in == "2":
            clear()
            # function asks for user input and returns the selected instance
            inst = list_instances()
            # Checks if at lease 1 instance was returned
            if inst is not None:
                # A try/except to prevent the script from crashing
                try:
                    # Will call function to ssh to instance and run the .py file stored on it
                    run_check_webserver(key_dir, inst[2])
                except Exception as error:
                    # prints out error to console for user
                    print(error)
                
            input("\nPress Enter to return to menu...")
            return_menu()
        
        elif menu_in == "3":
            clear()
            add_header("Upload to Bucket")
            to_dir = input("Enter file path\n> ")
            #if os.path.exists(to_dir):
             #   list_buckets()
            print(os.path.exists(to_dir))
            return_menu()
        
        # runs new_instance() without the new_bucket()
        elif menu_in == "4":
            new_instance()
            return_menu()

        # runs new_instance() without the new_bucket()
        elif menu_in == "5":
            clear()
            new_bucket()
            return_menu()
        
        # exits and ends script
        elif menu_in == "ex":
            print("\nExiting...")
            time.sleep(3)
            print("Goodbye.")
            break
            
        else:
            continue
    
if __name__ == "__main__":
    main()