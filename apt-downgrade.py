#!/usr/bin/env python

def user_proceed(prompt, default=True):
    if default == True and opts.yes:
        return True
    while True:
        rin = raw_input(prompt)
        if not rin:
            return default
        if "yes".startswith(rin.lower()):
            return True
        if "no".startswith(rin.lower()):
            return False

def pick_origin(pkgver):
    goodors = filter(lambda x: x.archive != "now", pkgver.origins)
    assert len(goodors) == 1
    return goodors[0]

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-u", "--update", action="store_true", default=False,
        help="update the package cache first")
parser.add_option("-y", "--yes", action="store_true", default=False,
        help="assume yes to all questions for which yes is the default")
opts, args = parser.parse_args()

import apt, apt.progress
cache = apt.Cache()
if opts.update:
    print "Updating package cache..."
    cache.update(apt.progress.TextFetchProgress())
for pkg in cache:
    if pkg.installed and not pkg.candidate.downloadable:
        cand = None
        for ver in pkg.versions:
            if ver.downloadable and ver > cand:
                cand = ver
        #print pkg.installed, "->", cand
        if cand != None:
            if user_proceed(
                    "Force '%s' version\n\tfrom %s\n\tto   %s (source: %s) [y]: "
                    % ( pkg.name,
                        pkg.installed.version,
                        cand.version,
                        pick_origin(cand).archive)):
                pkg.candidate = cand
                pkg.mark_install(autoFix=False, fromUser=False)
            #pkg.mark_upgrade()
print "The following changes will be made..."
if cache.get_changes():
    for pkg in cache.get_changes():
        print "\t%s %s => %s (source: %s)" % (
                pkg.name,
                pkg.installed and pkg.installed.version,
                pkg.candidate.version,
                pick_origin(pkg.candidate).archive)
    print "%i bytes will be downloaded" % (cache.required_download)
    if user_proceed("Do you wish to make the changes above? [n]", default=False):
        cache.commit(apt.progress.TextFetchProgress(), apt.progress.InstallProgress())
    else:
        print "User cancelled."
else:
    print "There are no changes to be made."
