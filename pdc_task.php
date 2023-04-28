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
	'pgcc'
    );
    public $compiler_index;  /* use index to avoid injection attack */
    public $scriptDir = "/shared/pdc-script";
    public $scriptFileName = "standalone";
    
    function rab_log($msg) {
	$log = fopen("/shared/rab_log", "a");
	fwrite($log, date("*** md_his: ") . $msg . "\n");
	fclose($log);
    }

    public function __construct($filename, $input, $params) {
//	$this->rab_log('[' . implode('   ', $params) . ']');	
        parent::__construct($filename, $input, $params);
	$this->rab_log('[' . implode('   ', $this->params) . ']');	
	$this->rab_log('[' . implode('   ', $params) . ']');	
        $this->default_params['compiler'] = 'g++';
        $this->default_params['compileargs'] = array(
            '-Wall',
            '-Werror');
    }

    public static function getVersionCommand() {
        return array('echo 0.1', '/([0-9.]*)/');
    }

    public function compile() {
        $this->executableFileName = $this->sourceFileName;
//	$this->rab_log($this->scriptDir . " " . $this->scriptFileName);	
	$this->rab_log('compiler = ' . $this->getParam('compiler', true));
	if (isset($this->params))  // DEBUG
	    $this->rab_log(count($this->params));
	else
	    $this->rab_log('$this->params not set!');
	$this->rab_log('compileargs = ' . implode('  ', $this->getParam('compileargs')));	
//	$this->rab_log('[' . $this->params . ']');	
	$this->compiler_index = array_search($this->getParam('compiler'),
			                     $this->supported_compilers);	
	$this->rab_log('compiler_index = ' . strval($this->compiler_index));
	chmod($this->executableFileName, 0755);
    }


    // A default name for C++ programs
    public function defaultFileName($sourcecode) {
        return 'prog';
   }


    // The executable is the output from the compilation
    public function getExecutablePath() {
        return "./" . $this->executableFileName;
    }


    public function getTargetFile() {
        return $this->sourceFileName;
    }
};
