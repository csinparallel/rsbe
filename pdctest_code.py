# sample source codes for pdctest.py

C_CODE = r"""
#include <stdio.h>
int main() {
    printf("Hello world\nIsn't this fun!\n");
}
"""


LONG_C = r"""
#include <stdio.h>
#include <unistd.h>
int main() {
  const int min = 5;
  int n;
  for (n = 0;  n < min*60;  n++) {
    printf(".");
    if (n%10 == 0)
      printf("\n");
    sleep(1);
  }
  printf("Exiting after %d minutes\n", min);
  return (0);
}
"""


CPP_CODE = """
#include <iostream>
#define MESSAGE "Hello Jobe!"
using namespace std;

int main() {
    cout << MESSAGE << endl;
}
"""


LONG_C = r"""
#include <stdio.h>
#include <unistd.h>
int main() {
  const int min = 5;
  int n;
  for (n = 0;  n < min*60;  n++) {
    printf(".");
    if (n%10 == 0)
      printf("\n");
    sleep(1);
  }
  printf("Exiting after %d minutes\n", min);
  return (0);
}
"""




TRAP_OMP_C = r"""
#include <math.h>
#include <stdio.h>    // printf()
#include <stdlib.h>   // atoi()
#include <omp.h>      // OpenMP


/* Demo program for OpenMP: computes trapezoidal approximation to an integral*/

const double pi = 3.141592653589793238462643383079;

int main(int argc, char** argv) {
  /* Variables */
  double a = 0.0, b = pi;  /* limits of integration */;
  int n = 1048576; /* number of subdivisions = 2^20 */
  double h = (b - a) / n; /* width of subdivision */
  double integral; /* accumulates answer */
  int threadct = 1;
  
  double f(double x);
  
   /* parse command-line arg for number of threads */
  if (argc > 1) {
	  threadct = atoi(argv[1]);
  }
    
#ifdef _OPENMP
  omp_set_num_threads( threadct );
  printf("OMP defined, threadct = %d\n", threadct);
#else
  printf("OMP not defined");
#endif

  integral = (f(a) + f(b))/2.0;
  int i;

  for(i = 1; i < n; i++) {
    integral += f(a+i*h);
  }
  
  integral = integral * h;
  printf("With %d trapezoids,  our estimate of the integral from \n", n);
  printf("%f to %f is %f\n", a,b,integral);
}
   
double f(double x) {
  return sin(x);
}
"""


TRAP_OMP_CPP = r"""
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

MPI_SPMD_C = r"""
/* spmd.c
 * ... illustrates the single program multiple data
 *      (SPMD) pattern using basic MPI commands.
 *
 * Joel Adams, Calvin College, November 2009.
 *
 * Usage: mpirun -np 4 ./spmd
 *
 * Exercise:
 * - Compile and run.
 * - Compare source code to output.
 * - Rerun, using varying numbers of processes
 *    (i.e., vary the argument to 'mpirun -np').
 * - Explain what "multiple data" values this
 *    "single program" is generating.
 */

#include <stdio.h>   // printf()
#include "/usr/lib/openmpi-4.1.5/include/mpi.h"     // MPI functions

int main(int argc, char** argv) {
    int id = -1, numProcesses = -1, length = -1;
    char myHostName[MPI_MAX_PROCESSOR_NAME];

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &id);
    MPI_Comm_size(MPI_COMM_WORLD, &numProcesses);
    MPI_Get_processor_name (myHostName, &length);

    printf("Greetings from process #%d of %d on %s\n",
             id, numProcesses, myHostName);

    MPI_Finalize();
    return 0;
}
"""


DD_MPI_CPP = r"""
#include <cmath>
#include <cstdlib>
#include <algorithm>
#include <iostream>
#include <sstream>
#include <string>
#include <queue>
#include <vector>
#include <mpi.h>

#define DEFAULT_max_ligand 7
#define DEFAULT_nligands 120
#define DEFAULT_nthreads 4
#define DEFAULT_protein "the cat in the hat wore the hat to the cat hat party"

#define MAX_BUFF 100
#define VERBOSE 0  // non-zero for verbose output

struct Pair {
  int key;
  std::string val;
  
  Pair(int k, const std::string& v) : key(k), val(v) {}
};

class Help {
public:
  static std::string get_ligand(int max_ligand);
  static int score(const char*, const char*);
};

class MR {
private:
  enum MsgType {
    GET_TASK, // worker request for a fresh ligand to score
    TASK_RESULT, // worker delivery of a score for a ligand
    ACK // protocol acknowledgment message
  };
  
  int max_ligand;
  int nligands;
  int nnodes;
  int rank;
  static const int root = 0;
  std::string protein;
  
  std::queue<std::string> tasks;
  std::vector<Pair> results;
  
  void Generate_tasks(std::queue<std::string>& q);
  //void Map(const std::string& str, std::vector<Pair>& pairs);
  void Sort(std::vector<Pair>& vec);
  int Reduce(int key, const std::vector<Pair>& pairs, int index, 
	     std::string& values);
  
public:
  const std::vector<Pair>& run(int ml, int nl, const std::string& p);
};

int main(int argc, char **argv) {
  int max_ligand = DEFAULT_max_ligand;
  int nligands = DEFAULT_nligands;
  std::string protein = DEFAULT_protein;
  
  if (argc > 1)
    max_ligand = strtol(argv[1], NULL, 10);
  if (argc > 2)
    nligands = strtol(argv[2], NULL, 10);
  if (argc > 3)
    protein = argv[4];
  // command-line args parsed
  
  MPI_Init(&argc, &argv);
  
  MR map_reduce;
  std::vector<Pair> results = map_reduce.run(max_ligand, nligands, protein);
  
  if(results.size()) {
    std::cout << "maximal score is " << results[0].key 
	      << ", achieved by ligands " << std::endl 
	      << results[0].val << std::endl;
  }
  
  MPI_Finalize();
  
  return 0;
}

const std::vector<Pair>& MR::run(int ml, int nl, const std::string& p) {
  max_ligand = ml;
  nligands = nl;
  protein = p;
  
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Comm_size(MPI_COMM_WORLD, &nnodes);
  
  char buff[MAX_BUFF];
  
  MPI_Status status;
  
  char empty = 0;
  
  if(rank == root) {
    // Only the root will generate the tasks
    Generate_tasks(tasks);
    
    // Keep track of which workers are working
    std::vector<int> finished;
    for(int i = 0; i < nnodes; ++i) {
      finished.push_back(0);
    }
    finished[root] = 1;  // master task does no scoring
    
    std::vector<Pair> pairs;
    
    // The root waits for the workers to be ready for processing
    // until all workers are done
    while([&](){ 
	for(auto i : finished) { if(!i) return 1; } 
	return 0; }()) {
      
      MPI_Recv(buff, MAX_BUFF, MPI_CHAR, MPI_ANY_SOURCE, MPI_ANY_TAG, 
	       MPI_COMM_WORLD, &status);
      switch(status.MPI_TAG) {

      case GET_TASK:
	// Send the next task to be processed
	if(tasks.empty()) {
	  MPI_Send((void*)&empty, 1, MPI_CHAR, status.MPI_SOURCE, ACK, 
		   MPI_COMM_WORLD);
	  
	  // Mark the worker as finished
	  finished[status.MPI_SOURCE] = 1;
	} else {
	  MPI_Send((void*)tasks.front().c_str(), tasks.front().size() + 1, 
		   MPI_CHAR, status.MPI_SOURCE, ACK, MPI_COMM_WORLD);
	  tasks.pop();
	}
	break;

      case TASK_RESULT: {
	std::string buffstr(buff);
	std::stringstream stream(buffstr);
	std::string task;
	int score;
	
	stream >> task;
	stream >> score;
	pairs.push_back(Pair(score, task));
	if (VERBOSE) 
	  std::cout << rank << ": " << task << " --> " << score << 
	    " (received from " << status.MPI_SOURCE << ")" << std::endl;

      }
	break;

      default:
	break;
      }
    }
    
    // All tasks are done
    Sort(pairs);
    
    int next = 0;
    while(next < pairs.size()) {
      std::string values("");
      int key = pairs[next].key;
      next = Reduce(key, pairs, next, values);
      Pair p(key, values);
      results.push_back(Pair(key, values));
    }

  } else {
    // code for workers
    while(1) {
      
      // Receive the next task
      MPI_Send((void*)&empty, 1, MPI_CHAR, root, GET_TASK, MPI_COMM_WORLD);
      MPI_Recv(buff, MAX_BUFF, MPI_CHAR, root, ACK, MPI_COMM_WORLD, &status);
      
      if(!buff[0]) {
	// No more tasks to process
	break;
      } else {
	// Process the task
	std::string task(buff);
	int score = Help::score(task.c_str(), protein.c_str());
	if (VERBOSE) 
	  std::cout << rank << ": score(" << task.c_str() << 
	    ", ...) --> " << score << std::endl;
	
	// Send back to root, serialized as a stringstream
	std::stringstream stream;
	stream << task << " " << score;
	MPI_Send((void*)stream.str().c_str(), stream.str().size() + 1, MPI_CHAR, root, TASK_RESULT, MPI_COMM_WORLD);
      }
    }
  }
  
  return results;
}

void MR::Generate_tasks(std::queue<std::string> &q) {
  for (int i = 0;  i < nligands;  i++) {
    q.push(Help::get_ligand(max_ligand));
  }
}


void MR::Sort(std::vector<Pair>& vec) {
  std::sort(vec.begin(), vec.end(), [](const Pair& a, const Pair& b) {
      return a.key > b.key;
    });
}

int MR::Reduce(int key, const std::vector<Pair>& pairs, int index, std::string& values) {
  while(index < pairs.size() && pairs[index].key == key) {
    values += pairs[index++].val + " ";
  }
  
  return index;
}

std::string Help::get_ligand(int max_ligand) {
  int len = 1 + rand()%max_ligand;
  std::string ret(len, '?');
  for (int i = 0;	i < len;	i++)
    ret[i] = 'a' + rand() % 26;	
  return ret;
}


int Help::score(const char *str1, const char *str2) {
  if (*str1 == '\0' || *str2 == '\0')
    return 0;
  // both argument strings non-empty
  if (*str1 == *str2)
    return 1 + score(str1 + 1, str2 + 1);
  else // first characters do not match
    return std::max(score(str1, str2 + 1), score(str1 + 1, str2));
}
"""


CUDA_DEVICE_INFO_CU = r"""
/*
 *  Use cuda functions to print device information.
 */
// System includes
#include <stdio.h>

// helper functions and utilities to work with CUDA
int _ConvertSMVer2Cores(int major, int minor);
void getDeviceInformation();


int main(int argc, char **argv) {
  
  // shows how many SMs on our device, among other things
  getDeviceInformation();   

  return 0;
}

////////// Details below here.  /////////////////////////////
//
// If you are interested in some details about the CUDA library
// functions that help us find out about the device we are running 
// code on, you can look at the detail below.

/*
 *  Functions for checking info about a GPU device.
 */
 
 // taken from help_cuda.h from the NVIDIA samples.
 // Used to determine how many cores we have for the
 // GPU's partucular architecture.
 //
 inline int _ConvertSMVer2Cores(int major, int minor) {
  // Defines for GPU Architecture types (using the SM version to determine
  // the # of cores per SM
  typedef struct {
    int SM;  // 0xMm (hexidecimal notation), M = SM Major version,
    // and m = SM minor version
    int Cores;
  } sSMtoCores;

  sSMtoCores nGpuArchCoresPerSM[] = {
      {0x30, 192},
      {0x32, 192},
      {0x35, 192},
      {0x37, 192},
      {0x50, 128},
      {0x52, 128},
      {0x53, 128},
      {0x60,  64},
      {0x61, 128},
      {0x62, 128},
      {0x70,  64},
      {0x72,  64},
      {0x75,  64},
      {0x80,  64},
      {0x86, 128},
      {0x87, 128},
      {0x89, 128},
      {0x90, 128},
      {-1, -1}};

  int index = 0;

  while (nGpuArchCoresPerSM[index].SM != -1) {
    if (nGpuArchCoresPerSM[index].SM == ((major << 4) + minor)) {
      return nGpuArchCoresPerSM[index].Cores;
    }

    index++;
  }

  // If we don't find the values, we default use the previous one
  // to run properly
  printf(
      "MapSMtoCores for SM %d.%d is undefined."
      "  Default to use %d Cores/SM\n",
      major, minor, nGpuArchCoresPerSM[index - 1].Cores);
  
  return nGpuArchCoresPerSM[index - 1].Cores;

 }

// Find out info about a GPU.
// See this page for list of all the values we can "query" for:
// https://rdrr.io/github/duncantl/RCUDA/man/cudaDeviceGetAttribute.html
//
void getDeviceInformation() {
  int devId;            // the number assigned to the GPU
  int memSize;          // shared mem in each streaming multiprocessor (SM)
  int numProcs;         // number of SMs
  
  struct cudaDeviceProp props;

  cudaGetDevice(&devId);
  
  // can get one by one like this
  cudaDeviceGetAttribute(&memSize, 
    cudaDevAttrMaxSharedMemoryPerBlock, devId);
  cudaDeviceGetAttribute(&numProcs,
    cudaDevAttrMultiProcessorCount, devId);
  
  // or we can get all the properties
  cudaGetDeviceProperties(&props, devId);

  // Then print those we are interested in
  printf("Device %d: \"%s\" with Compute %d.%d capability\n", devId, props.name,
         props.major, props.minor);

  char msg[256];
  snprintf(msg, sizeof(msg),
             "Total amount of global memory:      %.0f MBytes "
             "(%llu bytes)\n",
             static_cast<float>(props.totalGlobalMem / 1048576.0f),
             (unsigned long long)props.totalGlobalMem);

  printf("%s", msg);

  printf("GPU device shared memory per block of threads on an SM: %d bytes\n", memSize);
  printf("GPU device total number of streaming multiprocessors: %d\n", numProcs);

  printf("With %3d Multiprocessors (MPs), this device has %03d CUDA Cores/MP,\n for total of  %d CUDA Cores on this device.\n",
           props.multiProcessorCount,
           _ConvertSMVer2Cores(props.major, props.minor),
           _ConvertSMVer2Cores(props.major, props.minor) *
               props.multiProcessorCount);

  printf("\n");
  printf("Max dimension sizes of a grid (x,y,z): (%d, %d, %d)\n",
  props.maxGridSize[0], props.maxGridSize[1],
           props.maxGridSize[2]);
  
  printf("Max dimension sizes of a thread block (x,y,z): (%d, %d, %d)\n",
           props.maxThreadsDim[0], props.maxThreadsDim[1],
           props.maxThreadsDim[2]);

}
"""


CUDA_DIM3DEMO_CU = r"""
#include <stdio.h>
#include <cuda_runtime.h>

// !!!!!! NOTE:
//  NVIDIA refers to these functions prefaced with __global__ 
//  as 'kernel' functions that run on the GPU 'device'.
__global__ void hello() {
    // special dim3 variables available to each thread in a kernel
    // or device function:
    // blockIdx    the x, y, z coordinate of the block in the grid
    // threadIdX   the x, y, z coordinate of the thread in the block
    printf("I am thread (%d, %d, %d) of block (%d, %d, %d) in the grid\n",
           threadIdx.x, threadIdx.y, threadIdx.z, blockIdx.x, blockIdx.y, blockIdx.z );

}

// Note that this is called from the host, not the GPU device.
// We create dim3 structs there and can print their components
// with this function.
void printDims(dim3 gridDim, dim3 blockDim) {
    printf("Grid Dimensions : {%d, %d, %d} blocks. \n",
    gridDim.x, gridDim.y, gridDim.z);

    printf("Block Dimensions : {%d, %d, %d} threads.\n",
    blockDim.x, blockDim.y, blockDim.z);
}

int main(int argc, char **argv) {

    // dim3 is a special data type: a vector of 3 integers.
    // each integer is accessed using .x, .y and .z 
    // (see printDims() above)

       // 1 dimensionsional case a is the following: 1D grid of 1D block
    dim3 gridDim(1);      // 1 blocks in x direction, y, z default to 1
    dim3 blockDim(8);     // 8 threads per block in x direction

    // TODO: Try 128 threads in a block. What do you observe?
    //       Try the maximum threads per block allowed for your card.
    //       See device_info example.
    //       Try over the maximum threads per block for your card.
   
    printDims(gridDim, blockDim);
    
    printf("From each thread:\n");
    hello<<<gridDim, blockDim>>>();
    cudaDeviceSynchronize();     // need for printfs in kernel to flush

    return 0;
}
"""

ACC_CODE = r"""
#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <time.h>

// function declarations
void fillMatrix(int size, float * A);
void MatrixMult(int size, float * __restrict__ A, 
                   float * __restrict__ B, float * __restrict__ C);// 
void getArguments(int argc, char **argv, int *size, int *verbose);
void debugPrintMatrix(int verbose, int size, float *matrix, const char *msg);
void showMatrix(int size, float * matrix);

int main (int argc, char **argv) {
 
   // default values
   int size = 256;          // num rows, cols of square matrix
   int verbose = 0;         // default to not printing matrices
   getArguments(argc, argv, &size, &verbose); //change defaults

   float * A;  // input matrix
   float * B;  // input matrix
   float * C;  // output matrix

// Use a 'flattened' 1D array of contiguous memory for the matrices
// size = number of rows = number of columns in the square matrices
   size_t num_elements = size * size * sizeof(float);
   A = (float *)malloc(num_elements);
   B = (float *)malloc(num_elements);
   C = (float *)malloc(num_elements);

   fillMatrix(size, A);
   fillMatrix(size, B);
   char msgA[32] = "matrix A after filling:";
   debugPrintMatrix(verbose, size, A, msgA);
   
   // double startTime = omp_get_wtime();
   clock_t t_start, t_end;              // for timing
   t_start = clock();
   
   MatrixMult(size, A, B, C);

   char msgC[32] = "matrix C after MatrixMult(): ";
   debugPrintMatrix(verbose, size, C, msgC);
   
   // double endTime = omp_get_wtime();
   t_end = clock();
   double tot_time_secs = ((double)(t_end-t_start)) / CLOCKS_PER_SEC;
   // double tot_time = endTime - startTime;
   printf("%s total runtime %f seconds (%f milliseconds)\n", argv[0], tot_time_secs, tot_time_secs*1000);
   // printf("%s total omp runtime %f seconds (%f milliseconds)\n", argv[0], tot_time, tot_time*1000);

   free(A); free(B); free(C); 
   return 0;
}
////////////////////////////////////// end main

// fill a given square matrix with rows of float values 
// equal to each row number
void fillMatrix(int size, float * A) {
   for (int i = 0; i < size; ++i) {
      for (int j = 0; j < size; ++j) {
        A[i*size + j] = ((float)i);
      }
   }
}

// mutiply matrix A times matrix B, placing result in matrix C
// void MatrixMult(int size, float * __restrict__ A, 
//                float * __restrict__ B, float * __restrict__ C) {
void MatrixMult(int size, float * restrict A, 
               float * restrict B, float * restrict C) {
   
   float tmp = 0.;      // holds dot product for each cell of C

#pragma acc kernels pcopyin(A[0:size*size],B[0:size*size],C[0:size*size]) pcopyout(C[0:size*size])
#pragma acc loop collapse(2) independent private(tmp)
   for (int i = 0; i < size; ++i) {
     for (int j = 0; j < size; ++j) {
       tmp = 0.;
#pragma acc loop seq 
       for (int k = 0; k < size; ++k) {
          tmp += A[i*size + k] * B[k*size + i];
       }
       C[i*size + j] = tmp;    // update cell of C once
     }
   }
}

void getArguments(int argc, char **argv, int *size, int *verbose) {
   // 2 arguments optional: 
   //   size of one side of square matrix
   //   verbose printing for debugging
   if (argc > 3) {
      fprintf(stderr,"Use: %s [size] [verbose]\n", argv[0]);
      exit(EXIT_FAILURE);
   }

   if (argc >= 2) {
      *size = atoi(argv[1]);
      if (argc == 3) {
         *verbose = atoi(argv[2]);
      }
   }
   
   if (*verbose) {
      printf("size of matrix side: %d\n", *size);
   }
}

void debugPrintMatrix(int verbose, int size, float *matrix, const char *msg) {
   if (verbose){
      printf("%s \n", msg);
      showMatrix(size, matrix);
   }
}

// display a given square matrix for debugging purposes
void showMatrix(int size, float * matrix) {
   int i, j;
   for (i=0; i<size; i++){
      for (j=0; j<size; j++) {
         printf("element [%d][%d] = %f \n",i,j, matrix[i*size + j]);
      }
   }
}
"""


CHPL_CODE = r"""
writeln("Hello, world!");
"""
