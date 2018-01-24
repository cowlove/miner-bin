#!/usr/bin/perl

$minFail = 1;
$miners = "miner1 miner2 miner3 miner4";
@miners = split(' ', $miners);

$stime = 0;
while(<>) { 
	if (/(\d+) [FHM]RATE (\S+) ([0-9.\-]+)/) { 
		if ($stime == 0) { $stime = $1 - ($1 % 3600) }
		if ($3 > 0) {
			$rates{$2} = $3;
			$consecFail{$2} = 0;
		} else {
			$consecFail{$2} = $consecFail{$2} + 1;
			if ($consecFail{$2} > $minFail) {
				$rates{$2} = $3;
			} 
		}
		$line = "" . $1 - $stime . " ";
		foreach $m (@miners) { 
			$rates{$m} = $rates{$m} + 0;
			$line = $line . " $rates{$m}"; 
		}
		$line = $line . "\n";
		print $line;
	}
}
