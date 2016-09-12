#!/usr/bin/perl -w

use strict;

my ($language) = @ARGV;

while(<STDIN>) {
    s/ - / \@\-\@ /g;
    s/'/\&apos;/g;
    s/"/\&quot;/g;
    s/\[/\&#91;/g;
    s/\]/\&#93;/g;
    print $_;
}
