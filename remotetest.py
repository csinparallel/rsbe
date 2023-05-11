#! /usr/bin/env python3
''' remotetest.py - a simple demo of how to submit a program, for remote use
    to Jobe. Demonstrates python3, C++ and Java.
    Includes a call to get the list of languages.

    Adapted from Jobe distribution's simpletest.py by RAB
    4/25/23:  added test of pdc language (assumed still to be clone of C++)
        To test, enter
            ssh -L4000:localhost:4000 csinparallel.calvin.edu
        in a shell window, then enter
            python3 remotetest.py
        in another shell window
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

PYTHON_CODE = """
MESSAGE = 'rabtest: Hello, Jobe!'

def sillyFunc(message):
    '''Pointless function that prints the given message'''
    print("Message is", message)

sillyFunc(MESSAGE)
"""

CPP_CODE = """
#include <iostream>
#define MESSAGE "Hello Jobe!"
using namespace std;

int main() {
    cout << MESSAGE << endl;
}
"""


PDC_CODE = r"""
#include <iostream>
#include <cmath>
#include <cstdlib>
using namespace std;

/* Demo program for OpenMP: computes trapezoidal approximation to an integral*/

const double pi = 3.141592653589793238462643383079;

int main(int argc, char** argv) {
  /* Variables */
  double a = 0.0, b = pi;  /* limits of integration */;
  int n = 1048576; /* number of subdivisions = 2^20 */
  double h = (b - a) / n; /* width of subdivision */
  double integral; /* accumulates answer */
  int threadct = 1;  /* number of threads to use */
  
  /* parse command-line arg for number of threads */
  if (argc > 1)
    threadct = atoi(argv[1]);

  double f(double x);
    
#ifdef _OPENMP
  cout << "OMP defined, threadct = " << threadct << endl;
#else
  cout << "OMP not defined" << endl;
#endif

  integral = (f(a) + f(b))/2.0;
  int i;
#pragma omp parallel for num_threads(threadct) \
     shared (a, n, h) reduction(+:integral) private(i)
  for(i = 1; i < n; i++) {
    integral += f(a+i*h);
  }
  
  integral = integral * h;
  cout << "With n = " << n << " trapezoids, our estimate of the integral" <<
    " from " << a << " to " << b << " is " << integral << endl;
}
   
double f(double x) {
  return sin(x);
}
"""


JAVA_CODE = """
public class Blah {
    public static void main(String[] args) {
        System.out.println("Farewell cruel world");
    }
}
"""

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



def run_test(language, code, filename):
    '''Execute the given code in the given language.
       Return the result object.'''
    runspec = {
        'language_id': language,
        'sourcefilename': filename,
        'sourcecode': code,
    }

    resource = '/jobe/index.php/restapi/runs/'
    data = json.dumps({ 'run_spec' : runspec })
    response = None
    content = ''
    result = do_http('POST', resource, data)
    return result

def run_test_pdc(runspec):
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
    '''Demo or get languages, a run of Python3 then C++ then Java'''
    print("Jobe server:  " + JOBE_SERVER)
    print("Supported languages:")
    resource = '/jobe/index.php/restapi/languages'
    lang_versions = do_http('GET', resource)
    for lang, version in lang_versions:
        print("    {}: {}".format(lang, version))
    print()
    print("Running python...")
    result_obj = run_test('python3', PYTHON_CODE, 'test.py')
    display_result(result_obj)
    print("\n\nRunning C++")
    result_obj = run_test('cpp', CPP_CODE, 'test.cpp')
    display_result(result_obj)
    print("\n\nRunning Java")
    result_obj = run_test('java', JAVA_CODE, 'Blah.java')
    display_result(result_obj)


    print("\n\nRunning PDC/g++")
    result_obj = run_test_pdc({
        'language_id': 'pdc',
        'sourcefilename': 'trap-omp.cpp',
        'sourcecode': PDC_CODE,
        'parameters': {
            'compiler': 'g++',
            'runargs' : '8',
            'compileargs': '-lm -fopenmp', 
        },
    })
    display_result(result_obj)

main()

