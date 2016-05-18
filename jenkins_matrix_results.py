#!/usr/bin/env python

'''
Uses jenkinsapi to query jenkins results for matrix configuration job.

Usage:
    python jenkins_matrix_results.py

Update jenkins_url, username, and api_key below. 
- Username is your E-mail address (listed on user page)
- To get your api key, open Jenkins, click on your username,
  click on Configure. Locate API Token section. Find / generate
  key here.

Script's approach to collecting results:
- Get list of most recent completed builds
- For each build, get a list of all matrix configurations that ran in the build
- For each run, add the build description to a matrix of results *unless*
  a set of results for that particular configuration has already been recorded
- Continue collecting results until either 1) all configurations are accounted for or
  2) the number of runs reviewed is greater than double the number of matrix configurations
     (this is just a heuristic to try to give the job a stopping point in case it can't
      find all results)

Known limitations:
- If results for a build are missing, output isn't correct
- Script collects results for last run of a configuration even if that run
  happened over a day ago.
'''

import sys
import re
from jenkinsapi.jenkins import Jenkins

# Jenkins connection information
jenkins_url = 'http://jenkins.company.com' 
username = 'user@email.com'
api_key = 'my_token' 
job_name = 'Test_Tower_Integration'

num_platforms = 8
num_ansible_versions = 3

result_count = 0
results = dict()
table_padding = 23 

def ansible_version_weight(version):
    '''Hack to set order of columns'''
    weight = {'devel': 0, 'stable-2.1': 1, 'stable-1.9': 2}
    return weight[version]

def platform_weight(platform):
    '''Hack to set order of platforms'''
    weight = {'rhel-6.7-x86_64': 0,        'rhel-7.2-x86_64': 1,
              'centos-6.latest-x86_64': 2, 'centos-7.latest-x86_64': 3,
              'ubuntu-12.04-x86_64': 4,    'ubuntu-14.04-x86_64': 5,
              'ol-6.7-x86_64': 6,          'ol-7.2-x86_64': 7}
    return weight[platform]


def add_result(job_description):
    '''Use description to add results for a given configuration. Returns True if new result was added.'''

    # Parse description
    res = re.search("(.*) / (.*) \((.*)\)", job_description)
    if not res:
        print "Could not parse: ", job_description
        return False
    try:
        platform = res.group(1)
        ansible_version = res.group(2)
        description = res.group(3)
    except Exception:
        print "Could not parse: ", job_description
        return False
   
    # Store result
    if platform not in results.keys():
        results[platform] = dict()
    if ansible_version not in results[platform].keys():
        results[platform][ansible_version] = dict()
    else:
        # Result for this platform has already been added
        return False
    results[platform][ansible_version] = description

    return True

def print_results(results):
    '''Print results for all configurations'''
    platforms = sorted(results.keys(), key=platform_weight)
    ansible_versions = sorted(results[platforms[0]].keys(), key=ansible_version_weight)

    header = "".ljust(table_padding)
    for version in ansible_versions:
        header += version.ljust(table_padding)
    print header 

    # For each platform
    for platform in platforms:
        ansible_versions = sorted(results[platform].keys())
        line = platform.ljust(table_padding)

        # For each ansible version
        for ansible_version in ansible_versions:
            line += results[platform][ansible_version].ljust(table_padding)

        print line

# Collect information from Jenkins 
jenkins = Jenkins(baseurl=jenkins_url, username=username, password=api_key)
job = jenkins[job_name]
builds = job.get_build_dict()
build_ids = sorted(builds.keys(), reverse=True)

finished = False
num_runs = 0
for build_id in build_ids:
    if finished:
        break
    #print "Build ", build_id
    build = job.get_build(build_id)
    runs = build.get_matrix_runs()
    index = 0
    for run in runs:
        num_runs += 1
        desc = run.get_description()
        #print "%s: %s" % (index, desc)
        new_result = add_result(desc)
        if new_result:
            #print result_count
            sys.stdout.write('.')
            sys.stdout.flush()
            result_count += 1
            if result_count >= num_platforms * num_ansible_versions: 
               finished = True 
        index += 1

    # Max number of job runs to consider (twice size of matrix)
    if num_runs > num_platforms * num_ansible_versions * 2:
        break

print "\n"
print_results(results)
