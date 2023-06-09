#! /usr/bin/env python3
''' pdctest.py - a demo of how to submit a program to Jobe.
    Demonstrates C, C++, and all implemented compilers in PDC pseudolanguage;  
    Includes a call to get the list of languages.
'''

from urllib.error import HTTPError
import json
import http.client

API_KEY = '2AAA7A5415B4A9B394B54BF1D2E9D'  # A working (100/hr) key on Jobe2
USE_API_KEY = True
#JOBE_SERVER = 'jobe2.cosc.canterbury.ac.nz'
try:
    with open('.jobeport', 'r') as file:
        JOBE_PORT = file.read().rstrip()
except:
    JOBE_PORT = '4000'
JOBE_SERVER = 'localhost:' + JOBE_PORT

from pdctest_code import *


# =============================================================

def http_request(method, resource, data, headers):
    '''Send a request to Jobe with given HTTP method to given resource on
       the currently configured Jobe server and given data and headers.
       Return the connection object. '''
    if USE_API_KEY:
            headers["X-API-KEY"] = API_KEY
    connect = http.client.HTTPConnection(JOBE_SERVER)
    connect.request(method, resource, data, headers)
    return connect



def run_test(runspec):
    '''Execute the runspec
       Return the result object.'''

    resource = '/jobe/index.php/restapi/runs/'
    data = json.dumps({ 'run_spec' : runspec })
    response = None
    content = ''
    result = do_http('POST', resource, data)
    return result


def do_http(method, resource, data=None):
    """Send the given HTTP request to Jobe, return json-decoded result as
       a dictionary (or the empty dictionary if a 204 response is given).
    """
    result = {}
    headers = {"Content-type": "application/json; charset=utf-8",
               "Accept": "application/json"}
    try:
        connect = http_request(method, resource, data, headers)
        response = connect.getresponse()
        if response.status != 204:
            content = response.read().decode('utf8')
            if content:
                result = json.loads(content)
        connect.close()

    except (HTTPError, ValueError) as e:
        print("\n***************** HTTP ERROR ******************\n")
        if response:
            print(' Response:', response.status, response.reason, content)
        else:
            print(e)
    return result


def trim(s):
    '''Return the string s limited to 10k chars'''
    MAX_LEN = 10000
    if len(s) > MAX_LEN:
        return s[:MAX_LEN] + '... [etc]'
    else:
        return s


def display_result(ro):
    '''Display the given result object'''
    if not isinstance(ro, dict) or 'outcome' not in ro:
        print("Bad result object", ro)
        return

    outcomes = {
        0:  'Successful run',
        11: 'Compile error',
        12: 'Runtime error',
        13: 'Time limit exceeded',
        15: 'Successful run',
        17: 'Memory limit exceeded',
        19: 'Illegal system call',
        20: 'Internal error, please report',
        21: 'Server overload'}

    code = ro['outcome']
    print("{}".format(outcomes[code]))
    print()
    if ro['cmpinfo']:
        print("Compiler output:")
        print(ro['cmpinfo'])
        print()
    else:
        if ro['stdout']:
            print("Output:")
            print(trim(ro['stdout']))
        else:
            print("No output")
        if ro['stderr']:
            print()
            print("Error output:")
            print(trim(ro['stderr']))



def main():
    '''Demo or get languages, runs of C and C++ then PDC'''
    print("Jobe server:  " + JOBE_SERVER)
    print("Supported languages:")
    resource = '/jobe/index.php/restapi/languages'
    lang_versions = do_http('GET', resource)
    for lang, version in lang_versions:
        print("    {}: {}".format(lang, version))
    print()

    print("\n\nRunning C")
    result_obj = run_test({
        'language_id': 'c',
        'sourcefilename': 'test.c',
        'sourcecode': C_CODE
    })
    display_result(result_obj)

    print("\n\nRunning C++ (2)")
    result_obj = run_test({
        'language_id': 'cpp',
        'sourcefilename': 'test.cpp',
        'sourcecode': CPP_CODE
    })
    display_result(result_obj)

    print("\n\nRunning PDC/gcc")
    result_obj = run_test({
        'language_id': 'pdc',
        'sourcefilename': 'trap-omp.c',
        'sourcecode': TRAP_OMP_C,
        'parameters': {
            'compiler': 'gcc',
            'runargs' : '8',
            'compileargs': '-lm -fopenmp', 
        },
    })
    display_result(result_obj)

    print("\n\nRunning PDC/g++")
    result_obj = run_test({
        'language_id': 'pdc',
        'sourcefilename': 'trap-omp.cpp',
        'sourcecode': TRAP_OMP_CPP,
        'parameters': {
            'compiler': 'g++',
            'runargs' : '8',
            'compileargs': '-lm -fopenmp', 
        },
    })
    display_result(result_obj)

    print("\n\nRunning PDC/g++ (2)")
    result_obj = run_test({
        'language_id': 'pdc',
#        'sourcefilename': 'trap-omp.cpp',
        'sourcecode': TRAP_OMP_CPP,
        'parameters': {
            'compiler': 'g++',
            'runargs' : ['8'],
            'compileargs': ['-lm', '-fopenmp'], 
        },
    })
    display_result(result_obj)

# new items


    print("\n\nRunning PDC/mpicc")
    result_obj = run_test({
        'language_id': 'pdc',
        'sourcefilename': 'mpi_spmd.c',
        'sourcecode': MPI_SPMD_C,
        'parameters': {
            'compiler': 'mpicc',
            'interpreterargs' : [
                '-map-by node',
                '-np 4',
            ],
        },
    })
    display_result(result_obj)


    print("\n\nRunning PDC/mpic++")
    result_obj = run_test({
        'language_id': 'pdc',
        'sourcefilename': 'dd_mpi.cpp',
        'sourcecode': DD_MPI_CPP,
        'parameters': {
            'compiler': 'mpic++',
            'compileargs': [
                '-std=c++11',
            ],
            'interpreterargs' : [
                '-map-by node',
                '-np 8',
            ],
            'runargs' : [
                '5',
                '100',
            ],
        },
    })
    display_result(result_obj)


    print("\n\nRunning PDC/nvcc")
    result_obj = run_test({
        'language_id': 'pdc',
        'sourcefilename': 'cuda_device_info.cu',
        'sourcecode': CUDA_DEVICE_INFO_CU,
        'parameters': {
            'compiler': 'nvcc',
            # no compileargs - note that -arch=... is automatic and server-side
            # no runargs or interpreterargs
        },
    })
    display_result(result_obj)


    print("\n\nRunning PDC/nvcc")
    result_obj = run_test({
        'language_id': 'pdc',
        'sourcefilename': 'cuda_dim3Demo.cu',
        'sourcecode': CUDA_DIM3DEMO_CU,
        'parameters': {
            'compiler': 'nvcc',
        },
    })
    display_result(result_obj)


    print("\n\nRunning PDC/pgcc")
    result_obj = run_test({
        'language_id': 'pdc',
        'sourcefilename': 'matrix_ex_float_acc.c',
        'sourcecode': ACC_CODE,
        'parameters': {
            'compiler': 'pgcc',
            'runargs': [
                1000,
                20,
                0
            ],
        },
    })
    display_result(result_obj)



main()

