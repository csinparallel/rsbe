<?php defined('BASEPATH') OR exit('No direct script access allowed');

/* ==============================================================
 *
 * PDC
 *
 * ==============================================================
 *
 * @copyright  2014 Richard Lobb, University of Canterbury
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 * adapted from cpp_task.php by rab@stolaf.edu, March-May 2023
 */

/* In this "pseudo language", parallel and distributed computations are
   performed on another server, a Runestone Backend (RSBE), instead of
   being performed on the Jobe server itself.  When Jobe receives a PDC
   request from Runestone, Jobe invokes an application $this->execpdc that
   transmits the requested to RSBE and delivers the results of the desired 
   PD computation, which Jobe relays to Runestone.

   The runspec for a PDC request must include a "compiler" value that
   signals a type of PD computation to perform, listed in
   $this->supported_compilers, plus standard runspec values and parameters
   intended for desired PD computation on RSBE (vs. $this->execpdc on Jobe) */

require_once('application/libraries/LanguageTask.php');

/* helper function, a generalization of array_merge() for assembling
   command lines, etc.
   The argument $value may be a single value or a (possibly nested) array
   of values.  The function returns a combined single string consisting of
   all values in depth-first order, separated by spaces.  */
   
function pdc_flatten($value) {
        if (is_array($value))
	    return implode(' ', array_map('pdc_flatten', $value));
	else
	    return strval($value);
}

class PDC_Task extends Task {
    public $supported_compilers = array(
    	'g++',
	'gcc',
	'mpicc',
	'mpic++',
//	'mpi4py',
	'nvcc',
	'nvcc++',
	'pgcc',
	'pgc++',
    );

    public $pdc_default_params = array(
        'g++' => array(
	    'pdc_backend' => 'omp', 
	    'pdc_ncores' => '4', 
	    'pdc_sourcefilename' => 'prog.cpp', 
            'pdc_autocompileargs' => array(
                '-Wall',
                '-Werror',
    	    ),
    	),
    
        'gcc' => array(
	    'pdc_backend' => 'omp', 
	    'pdc_ncores' => '4', 
	    'pdc_sourcefilename' => 'prog.c', 
            'pdc_autocompileargs' => array(
                '-Wall',
                '-Werror',
    	    ),
    	),
    
        'mpicc' => array(
	    'pdc_backend' => 'mpi', 
	    'pdc_nhosts' => '4', 
	    'pdc_ncores' => '2', 
	    'pdc_sourcefilename' => 'prog.c', 
            'pdc_interpreter' => 'mpirun',
	    'interpreter_choices' => array('mpirun', 'mpiexec'),
    	),
    	
        'mpic++' => array(
	    'pdc_backend' => 'mpi', 
	    'pdc_nhosts' => '4', 
	    'pdc_ncores' => '2', 
	    'pdc_sourcefilename' => 'prog.cpp', 
            'pdc_interpreter' => 'mpirun',
	    'interpreter_choices' => array('mpirun', 'mpiexec'),
    	),
    	
        'mpi4py' => array(
	    'pdc_backend' => 'mpi', 
	    'pdc_nhosts' => '4', 
	    'pdc_ncores' => '2', 
	    'pdc_sourcefilename' => 'prog.py', 
            'pdc_interpreter' => 'mpirun',
	    'interpreter_choices' => array('mpirun', 'mpiexec'),
            'pdc_interpreterexec' => 'python3',
    	),
    	
        'nvcc' => array(
	    'pdc_backend' => 'gpu', 
	    'pdc_sourcefilename' => 'prog.cu', 
            'pdc_autocompileargs' => array(
                '-arch=native',
//                '-arch=compute_61',
    	    ),
    	),
    	
        'nvcc++' => array(
	    'pdc_backend' => 'gpu', 
	    'pdc_sourcefilename' => 'prog.cu', 
            'pdc_autocompileargs' => array(
                '-arch=native',
//                '-arch=compute_61',
    	    ),
    	),
    	
        'pgcc' => array(
	    'pdc_backend' => 'gpu', 
	    'pdc_sourcefilename' => 'prog.c', 
            'pdc_autocompileargs' => array(
//                '-acc=gpu',
//                '-Minfo=accel',
//                '-arch=compute_61',
    	    ),
    	),
    	
        'pgc++' => array(
	    'pdc_backend' => 'gpu', 
	    'pdc_sourcefilename' => 'prog.cpp', 
            'pdc_autocompileargs' => array(
                '-acc=gpu',
                '-Minfo=accel',
//                '-arch=compute_61',
    	    ),
    	),
    	
    );
	
    public $cpl;  /* compiler */
    public $interpreter_choices;  
    public $execpdc= "/shared/execpdc/execpdc_client";
    
    function rab_log($msg) {
	$log = fopen("/shared/rab_log", "a");
	fwrite($log, date("*** md_his: ") . $msg . "\n");
	fclose($log);
    }

    public function __construct($filename, $input, $params) {
	$this->rab_log("******************************");
        parent::__construct($filename, $input, $params);
	$this->rab_log(print_r($this->params, true)); //DEBUG

	/* most received runspec values and parameters are intended for the
	   PD computation to perform on RSBE.  We will prepend "pdc_"
	   to the keys of such parameters, and use them in compile() to
	   specify the desired PD computation.  */ 
	if ($this->sourceFileName != "")
	   $this->params['sourcefilename']	= $this->sourceFileName;
	$this->sourceFileName = $this->defaultFileName(''); 
	foreach ($this->params as $key => $val)
	    if ($key != "compiler") {
	        $this->params["pdc_" . $key] = $val ;
		unset($this->params[$key]); }
        $this->default_params['compiler'] = 'g++';
	
	/* TEST VALIDITY HERE - THROW EXCEPTION IF NOT IN $supported_compilers*/

	/* set defaults for params pdc_*: first generic then compiler-specific*/
	foreach(array('nhosts', 'ncores', 
		      'compileargs', 'autocompileargs', 'linkargs', 
		      'interpreter', 'interpreterargs', 'interpreterexec',
		      'runargs') as $name)
	    $this->default_params["pdc_$name"] = '';
	$cpl_default_params =
	    $this->pdc_default_params[$this->getParam('compiler')];
	foreach ($cpl_default_params as $key => $val)
	    $this->default_params[$key] = $val;
//	$this->rab_log(print_r($this->default_params['pdc_compileargs'], true));

	if (isset($cpl_default_params['interpreter_choices']) &&
	        is_array($cpl_default_params['interpreter_choices']))
	    $this->interpreter_choices =
	        $cpl_default_params['interpreter_choices'];
	else
	    $this->interpreter_choices = false;
    }

    public static function getVersionCommand() {
        return array('echo 0.2', '/([0-9.]*)/');
    }

    public function compile() {
//	$code = file_get_contents($this->defaultFileName(''));
//	$this->rab_log($code);
//	$this->rab_log($this->sourceFileName);
        $this->executableFileName = $this->execpdc;
	$this->cpl = $this->getParam('compiler');
	if ("$this->cpl" == "mpi4py")
	   $this->cpl = '';

	/* prepare first arguments for the $this->execpdc command line, which
	   will be assembled in getRunCommand() (defined in LanguageTask.php) */
	$this->default_params['interpreterargs'] = array(
            $this->id,
	);

	/* prepare final arguments for the $this->execpdc command line */
	$this->default_params['runargs'] = array(
            $this->id . "." . $this->getParam('compiler'),
	);

	/* prepare specification of the desired a PD computation (to be
	   performed by RSBE), and store that specification in target file
	   (i.e., next command-line argument) for $this->execpdc */

	$this->rab_log('cpl = ' . $this->cpl);
	// add error checking for the following
	$code = file_get_contents($this->sourceFileName);
	$pdc = array(
	    'codelen' => strval(strlen($code)),
	);
	foreach (array_keys($this->default_params) as $key)
	    if (substr($key, 0, 4) == "pdc_")
	        $pdc[substr($key,4)] = $this->getParam($key);
	if ($this->cpl == '')
	    $pdc['executable'] = $pdc['sourcefilename'];
	else 	
	    $pdc['executable'] = pathinfo($pdc['sourcefilename'],
					  PATHINFO_FILENAME);

//	$this->rab_log(print_r($pdc, true));  	//DEBUG

	if (!$this->interpreter_choices ||
	        !in_array($pdc['interpreter'], $this->interpreter_choices)) {
	    if ($this->interpreter_choices) {
	        // assert:  $this->interpreter_choices is non-empty array
		//    AND $pdc['interpreter'] is not in that array
		$this->rab_log("invalid interpreter: " . $pdc['interpreter']);
		// THROW EXCEPTION?? convey to user via do_run script?
	    }
	    $pdc['interpreter'] = '';
	    $pdc['interpreterargs'] = '';
	}

	/* compose execpdc input file from params and provided code */
	$tgt = fopen($this->getTargetFile(), "w");
	fwrite($tgt, $pdc['backend'] . "\n");
	fwrite($tgt, pdc_flatten(array(
		         $this->id,
#			 isset($pdc['nhosts']) ? $pdc['nhosts']: '', 
#			 isset($pdc['ncores']) ? $pdc['ncores']: '', 
			 $pdc['nhosts'],
			 $pdc['ncores'],
			 $pdc['codelen'],
			 $pdc['sourcefilename'] )) );
	if ("$this->cpl" != '') 
	  fwrite($tgt, pdc_flatten(array(" $this->cpl",
			 "-o",
			 $pdc['executable'],
			 $pdc['autocompileargs'],
			 $pdc['sourcefilename'],
		   	 $pdc['compileargs'],
			 $pdc['linkargs'] )) );
	fwrite($tgt, "\n");
	fwrite($tgt, trim(pdc_flatten(array(
		     	 $pdc['interpreter'],
			 $pdc['interpreterargs'],
		     	 $pdc['interpreterexec'],
			 "./" . $pdc['executable'],
			 $pdc['runargs']))) . "\n");
	fwrite($tgt, $code);
	fclose($tgt);

	$this->rab_log(
	  implode("", array_slice(file($this->getTargetFile()), 0, 6)) . "...");

    }



    // A default name for sourcecode files
    public function defaultFileName($sourcecode) {
        return 'SOURCE_CODE';
   }


    // The executable is the output from the compilation
    public function getExecutablePath() {
        return $this->execpdc;
    }

    public function getTargetFile() {
        return 'EXECPDC_INPUT';
    }

};

