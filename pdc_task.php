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
	'mpi',
	'mpi4py',
	'nvcc',
	'nvcc++',
	'pgcc',
    );
    public $cpl_index;  /* use index to avoid injection attack */
    public $script = "/shared/pdc-script/standalone";
    
    function rab_log($msg) {
	$log = fopen("/shared/rab_log", "a");
	fwrite($log, date("*** md_his: ") . $msg . "\n");
	fclose($log);
    }

    public function __construct($filename, $input, $params) {
        parent::__construct($filename, $input, $params);
//	$this->rab_log('[' . implode('   ', $this->params) . ']');	
        $this->default_params['compiler'] = 'g++';
        $this->default_params['compileargs'] = array(
            '-Wall',
            '-Werror');
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
	$this->cpl_index = $this->get_cpl_index();	
	$this->rab_log('cpl_index = ' . $this->cpl_index);
    }


    // A default name for C++ programs
    public function defaultFileName($sourcecode) {
        return 'prog';
   }


    // The executable is the output from the compilation
    public function getExecutablePath() {
        return $this->script;
    }


    public function getTargetFile() {
        return $this->sourceFileName;
    }
};
