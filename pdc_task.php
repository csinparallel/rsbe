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

    public function __construct($filename, $input, $params) {
        parent::__construct($filename, $input, $params);
        $this->default_params['compileargs'] = array(
            '-Wall',
            '-Werror');
    }

    public static function getVersionCommand() {
        return array('echo 0.1', '/([0-9.]*)/');
    }

    function rab_log($msg) {
	$log = fopen("/shared/rab_log", "a");
	fwrite($log, date("*** md_his: ") . $msg . "\n");
	fclose($log);
    }

    public function compile() {
        $this->executableFileName = $this->sourceFileName;
	$this->rab_log($this->executableFileName);	
	$this->rab_log(sprintf("%o", fileperms($this->executableFileName)));	
	if (chmod($this->executableFileName, 0755))
 	  $this->rab_log("chmod succeeded");
	else
 	  $this->rab_log("chmod failed");
	clearstatcache();
	$this->rab_log(sprintf("%o", fileperms($this->executableFileName)));
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
