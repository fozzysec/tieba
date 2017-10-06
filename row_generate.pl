#!/usr/bin/env perl
#
use utf8;
use Cwd qw(abs_path);
use File::Basename;
use File::Path qw(make_path);
use feature qw(say);
use open ':std', ':encoding(UTF-8)';
use Time::HiRes qw(usleep);

my $path = dirname(abs_path(__FILE__)).'/';
my $config_file = $path.'row_generate.conf';
open(FH, '<:encoding(utf8)', $config_file) or die $!;
my @config_content = <FH>;
chomp foreach(@config_content);
say foreach(@config_content);
die;
my @config = split(/:/, $config);
my $fuzz_keywords = $config[0];
my @keywords = split(/\|/, $config[1]);
my $lv = 16;
my $filter = 'filters/none.conf';
my $counter = 0;
my $tmpdir = '/tmp';
while($counter < 96){
	foreach my $keyword (@keywords){
		$counter++;
		#say("cd $path&&scrapy crawl tieba -s FILENAME=$fuzz_keywords/$counter.jl -s USER_RANK=$lv -s FILTER=$path$filter -a keywords='$keyword' -a fuzz_keywords='$fuzz_keywords'");
		system("cd $path&&scrapy crawl tieba -s FILENAME=$fuzz_keywords/$counter.jl -s USER_RANK=$lv -s FILTER=$path$filter -a keywords='$keyword' -a fuzz_keywords='$fuzz_keywords'");
	}
	usleep(30 * 60 * 1000);
}
system("$path/dedup.py $fuzz_keywords $tmpdir/$fuzz_keywords.jl");
system("$path/generator.rb $tmpdir/$fuzz_keywords.jl > $tmpdir/$fuzz_keywords.html");
system("mutt -e 'set content_type=text/html' -s '给白菜的秀萝～' $config[2] < $tmpdir/$fuzz_keywords.html");
