<?php defined('BASEPATH') OR exit('No direct script access allowed');

/* ==============================================================
 *
 * PDC
 *
 * ==============================================================
 *
 * @copyright  2014 Richard Lobb, University of Canterbury
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 * adapted from cpp_task.php by rab@stolaf.edu, March 2023
 */

require_once('application/libraries/LanguageTask.php');

class PDC_Task extends Task {
    public $supported_compilers = array(
    	'g++',
	'gcc',
//	'mpicc',
//	'mpic++',
//	'mpi4py',
//	'nvcc',
//	'nvcc++',
//	'pgcc',
    );

    public $pdc_default_params = array(
        'g++' => array(
	    'pdc_sourcefilename' => 'prog.cpp', 
            'pdc_autocompileargs' => array(
                '-Wall',
                '-Werror',
    	    ),
    	),
    
        'gcc' => array(
	    'pdc_sourcefilename' => 'prog.c', 
            'pdc_autocompileargs' => array(
                '-Wall',
                '-Werror',
    	    ),
    	),
    
        'mpicc' => array(
	    'pdc_sourcefilename' => 'prog.c', 
            'pdc_interpreter' => 'mpirun',
    	),
    	
        'mpic++' => array(
	    'pdc_sourcefilename' => 'prog.cpp', 
            'pdc_interpreter' => 'mpirun',
    	),
    	
        'mpi4py' => array(
	    'pdc_sourcefilename' => 'prog.py', 
    	),
    	
        'nvcc' => array(
	    'pdc_sourcefilename' => 'prog.cu', 
    	),
    	
        'nvcc++' => array(
	    'pdc_sourcefilename' => 'prog.cu', 
    	),
    	
        'pgcc' => array(
	    'pdc_sourcefilename' => 'prog.cu', 
    	),
    	
    );
	
    public $cpl;  /* compiler */
    public $execpdc= "/shared/pdc-script/standalone";
    
    function rab_log($msg) {
	$log = fopen("/shared/rab_log", "a");
	fwrite($log, date("*** md_his: ") . $msg . "\n");
	fclose($log);
    }

    public function __construct($filename, $input, $params) {
        parent::__construct($filename, $input, $params);
//	$this->rab_log(print_r($this->params, true));
	$this->params['sourcefilename'] = $this->sourceFileName;
	$this->sourceFileName = $this->defaultFileName(''); 
	foreach ($this->params as $key => $val)
	    if ($key != "compiler") {
	        $this->params["pdc_" . $key] = $val ;
		unset($this->params[$key]); }
        $this->default_params['compiler'] = 'g++';
	
	/* TEST VALIDITY HERE - THROW EXCEPTION IF NOT IN $supported_compilers*/

	/* set defaults for params pdc_*: first generic then compiler-specific*/
	foreach(array('compileargs', 'autocompileargs',
		      'interpreter', 'interpreterargs',
		      'runargs') as $name)
	    $this->default_params["pdc_$name"] = ''; 
	foreach ($this->pdc_default_params[$this->getParam('compiler')]
		as $key => $val)
	    $this->default_params[$key] = $val;
//	$this->rab_log(print_r($this->default_params['pdc_compileargs'], true));

	/* TEST VALIDITY HERE - check valid interpreter (per compiler) */

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
	$this->rab_log('cpl = ' . $this->cpl);
	// add error checking for the following
	$code = file_get_contents($this->sourceFileName);
	$pdc = array(
	    'codelen' => strval(strlen($code)),
	);
	foreach (array_keys($this->default_params) as $key)
	    if (substr($key, 0, 4) == "pdc_")
	        $pdc[substr($key,4)] = $this->getParam($key);
	$pdc['executable'] = pathinfo($pdc['sourcefilename'],PATHINFO_FILENAME);

//	$this->rab_log(print_r($pdc, true)); 

	/* compose execpdc input file from params and provided code */
	$tgt = fopen($this->getTargetFile(), "w");
	fwrite($tgt, "sta\n");
	fwrite($tgt, implode(" ", array(
		         "example1",
			 "$pdc[codelen] $pdc[sourcefilename]", 
 			 "$this->cpl",
			 "-o $pdc[executable]",
//			 "$pdc[autocompileargs]",
			 "$pdc[sourcefilename]",
		   	 "$pdc[compileargs]\n")));
	fwrite($tgt, "./$pdc[executable] $pdc[runargs]\n");
	fwrite($tgt, $code);
	fclose($tgt);

	$this->rab_log(file_get_contents($this->getTargetFile())); 

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
