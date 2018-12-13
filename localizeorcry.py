#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess

def prepare_strings_for_gettext(source, copy, i=[]):
    """wrap strings  with _() for gettext recognition"""
    with open(source) as src:
        f = src.readlines()
    out = open(copy, 'w')
    count_new = 0
    count_old = 0
    for line in f:
        #check for strings on ignore list (not sure how useful)
        if line.strip() in i:
            print("Ignore: {}".format(line))
        #find already converted strings, just for the record
        elif line.find('_(') > -1:
            count_old += 1
        #check for multiline strings
        elif line.find('("""') > -1:
            line = line.replace('"""','_("""')
            count_new += 1
            print("New line: %s" % line)
        elif line.find('""")') > -1 and not line.find('"""))') > -1:
            line = line.replace('"""','""")')
        #check for strings in print, show_message and input function
        elif line.find('.show_message(') > -1 or line.find('print(') > -1 or line.find('input(') > -1 or line.find('.log.') > -1:
            #replace first occurance of " with _("
            line = line.replace('"','_("',1)
            #insert ) after last occurance of "
            if line.rfind('"') > -1:
                line = line[:line.rfind('"')+1]+')'+line[line.rfind('"')+1:]
                count_new += 1
                print("New line: %s" % line)
        out.write(line)
    print("%d new translatable string(s) have been found and transformed gettext readable." % count_new)
    print("%d old string(s) found. Shh, everything is alright." % count_old)
    print("Saved in copy as %s" % copy)
    out.close()

def get_ignorelist(f):
    with open(f) as i:
        ignore = i.readlines()
    #cut whitespace
    ignorelist = [i.strip() for i in ignore]
    return ignorelist

def get_pot_code(f,out):
    command = ['xgettext',
                '-L','Python',
                '-j',
                '--no-location',
                '--omit-header',
                '-o', os.path.join('po', out),
                f]
    subprocess.run(command)
    print("Added strings from {} to {}.".format(f, out))
    
def get_pot_glade(f,out):
    command = ['xgettext',
                '--sort-output',
                '--keyword=translatable',
                '--language=Glade',
                '-j',
                '--no-location',
                '--omit-header',
                '-o', os.path.join('po', out),
                f]
    subprocess.run(command)
    print("Added strings from {} to {}.".format(f, out))

def update_po_files(t):
    os.chdir('po')
    for f in os.listdir():
        if f.endswith('.po') and not f.startswith('new_'):
            newfile = open('new_%s' % f, 'w')
            subprocess.run(['msgmerge', f, t],stdout=newfile)
            print("Saved updated %s as %s." % (f, 'new_%s' % f))
            newfile.close()
            subprocess.run(["msgattrib",
                            "--set-obsolete",
                            "--ignore-file=GPT.pot",
                            "-o", "new_{}".format(f),
                            "new_{}".format(f),
                            ])
    os.chdir('..')

def replace_source(old,new):
    while 1:
        yessir = input("The new source file is correct (you better check it, stupid!) and can safely replace the old one. (y/n) ")
        if yessir == "y":
            os.rename(new, old)
            print("%s is %s now." % (new, old))
            break
        elif yessir == "n":
            print("No. That's okay, too.")
            break
        else:
            print("Invalid input. Try again...")

def replace_new_po():
    while 1:
        yessir = input("The new .po files are absolutely fabulous and can safely replace the old ones. (y/n) ")
        if yessir == "y":
            os.chdir('po')
            for f in os.listdir():
                if f.startswith('new_'):
                    os.rename(f,f[4:])
                    print("%s is %s now." % (f,f[4:]))
            break
        elif yessir == "n":
            os.chdir('po')
            for f in os.listdir():
                if f.startswith('new_'):
                    os.remove(f)
                    print("%s deleted." % f)
            os.chdir('..')
            break
        else:
            print("Invalid input. Try again...")


if __name__ == "__main__":
    
    ignore = get_ignorelist("ignoredstrings")
    
    os.chdir("herostuff")
    #files containing translatable strings
    source_file = 'modules.py'
   
    source_copy =  source_file[:-3] + '_copy.py'
    transl_templ = 'GPT.pot'

    #save new python code as copy
    prepare_strings_for_gettext(source_file,
                                source_copy,
                                ignore,
                                )

    #find new strings in glade files and save these in template (.pot)
    get_pot_code(source_copy, transl_templ)
    get_pot_glade('ui/gopro.glade', transl_templ)
    get_pot_glade('ui/tlcalculator.glade', transl_templ)
    get_pot_glade('ui/appwindow.glade', transl_templ)
    get_pot_glade('ui/playerwindow.glade', transl_templ)
    get_pot_glade('ui/stack_window.glade', transl_templ)

    #update existing .po files with new strings
    update_po_files(transl_templ)

    #ask whether code is correct and can replace the original
    replace_source(source_file,source_copy)

    #ask whether files are correct enough to replace the originals
    replace_new_po()

    #NOTE to self: invoke new language: msginit --input=GPT.pot --locale=xx
    # xx=language code

