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
//	'mpi',
//	'mpi4py',
//	'nvcc',
//	'nvcc++',
//	'pgcc',
    );

    public $pdc_default_params = array(
        'g++' => array(
            'pdc_compileargs' => array(
                '-Wall',
                '-Werror',
    	    ),
    	),
    
        'gcc' => array(
            'pdc_compileargs' => array(
                '-Wall',
                '-Werror',
		'-std=c99',
    	    ),
    	),
    
        'mpi' => array(
            'pdc_interpreter' => 'mpirun',
    	),
    	
        'mpi4py' => array(
    	),
    	
        'nvcc' => array(
    	),
    	
        'nvcc++' => array(
    	),
    	
        'pgcc' => array(
    	),
    	
    );
	
    public $cpl_index;  /* use index to avoid injection attack */
    public $cpl;  /* compiler */
    public $script = "/shared/pdc-script/standalone";
    
    function rab_log($msg) {
	$log = fopen("/shared/rab_log", "a");
	fwrite($log, date("*** md_his: ") . $msg . "\n");
	fclose($log);
    }

    public function __construct($filename, $input, $params) {
        parent::__construct($filename, $input, $params);
//	$this->rab_log('[' . implode('   ', $this->params) . ']');
	$this->rab_log('$this->pdc_default_params start'); 
	$this->rab_log(print_r($this->pdc_default_params, true)); 
	$this->rab_log('$this->pdc_default_params end'); 
	$this->rab_log(print_r($this->params, true)); 
	foreach ($this->params as $key => $val)
	    if ($key != "compiler") {
	        $this->params["pdc_" . $key] = $val ;
		unset($this->params[$key]); }
	$this->rab_log(print_r($this->params, true)); 
        $this->default_params['compiler'] = 'g++';
	foreach ($this->pdc_default_params[$this->getParam('compiler')] as $key => $val)
	    $this->default_params[$key] = $val;
	$this->rab_log(print_r($this->default_params['pdc_compileargs'], true)); 
    }

    public static function getVersionCommand() {
        return array('echo 0.1', '/([0-9.]*)/');
    }

    public function get_cpl_index($string = NULL) {
    	if (is_null($string))
	    $string = $this->getParam('compiler');
	return  array_search($string, $this->supported_compilers);
    }

    public function compile() {
        $this->executableFileName = $this->script;
	$this->cpl = $this->getParam('compiler');
	$this->rab_log('cpl = ' . $this->cpl);
	$this->cpl_index = $this->get_cpl_index();	
	$this->rab_log('cpl_index = ' . $this->cpl_index);
    }


    // A default name for C++ programs
    public function defaultFileName($sourcecode) {
        return 'SCRIPT_TARGET';
   }


    // The executable is the output from the compilation
    public function getExecutablePath() {
        return $this->script;
    }


    public function getTargetFile() {
        return $this->sourceFileName;
    }
};
