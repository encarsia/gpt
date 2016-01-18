#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import errno
import glob
import getpass
import time
import shutil
import subprocess
import fileinput
import locale
import gettext

_ = gettext.gettext

try:
    import gi
    gi.require_version('Gtk','3.0')
    from gi.repository import Gtk
except:
    print(_("Could not load GTK+, only command-line version is available."))

class Handler:
    """Signal assignment for Glade"""
    
    ##### main application window #####
    
    def on_gpwindow_destroy(self,*args):
        Gtk.main_quit()

    #left toolbar (working directory)
    def on_changewdir_clicked(self,widget):
        win = FileChooserDialog()
        win.on_folder_clicked()
        cli.chkdir(win.selectedfolder)
        cli.stdir = os.getcwd()
        app.show_workdir()
        app.load_dircontent()
        cli.replace_wdir_config(win.selectedfolder)

    def on_refresh_wdir_clicked(self,widget):
        app.load_dircontent()

    def on_open_wdir_clicked(self,widget):
        subprocess.run(['xdg-open',cli.stdir])

    #right toolbar (memory card)
    def on_import_sd_clicked(self,widget):
        if cli.freespace(cli.cardpath,cli.stdir) is False:
            app.get_targetfolderwindow_content()
        else:
            app.builder.get_object("nospacemessage").run()
            cli.show_message(_("Failed to copy files. Not enough free space."))
        app.load_dircontent()

    def on_find_sd_clicked(self,widget):
        app.find_sd()

    def on_open_sd_clicked(self,widget):
        subprocess.run(['xdg-open',cli.cardpath])

    #sort columns in TreeView
    def on_col_dir_clicked(self,widget):
        widget.set_sort_column_id(0)
        
    def on_col_vid_clicked(self,widget):
        widget.set_sort_column_id(1)
        
    def on_col_img_clicked(self,widget):
        widget.set_sort_column_id(2)
        
    def on_col_storage_clicked(self,widget):
        widget.set_sort_column_id(3)

    def on_treeview_selection_changed(self,widget):
        row, pos = widget.get_selected()
        if pos != None:
            #abs path stored in 5th column in treestore, not displayed in treeview
            self.sel_folder = row[pos][4]
            app.activate_tl_buttons(row[pos][1],row[pos][2],row[pos][4],row[pos][6])

    #calculate timelapse
    def on_tlvideo_button_clicked(self,widget):
        app.builder.get_object("multwindow").show_all()
        
    def on_tlimage_button_clicked(self,widget):
        app.timelapse_img(self.sel_folder)

    def on_tlimage_sub_button_clicked(self,widget):
        app.timelapse_img_subfolder(self.sel_folder)

    ##### set multiplier window ##### 

    def on_mult_cancel_clicked(self,widget):
        app.builder.get_object("multwindow").hide_on_delete()

    def on_mult_ok_clicked(self,widget):
        mult = app.builder.get_object("mult_spinbutton").get_value()
        app.builder.get_object("multwindow").hide_on_delete()
        app.timelapse_vid(self.sel_folder,mult)

    ##### select destination folder window ####

    def on_targetfolder_cancel_clicked(self,widget):
        app.builder.get_object("targetfolderwindow").hide_on_delete()

    def on_targetfolder_ok_clicked(self,widget):
        app.builder.get_object("targetfolderwindow").hide_on_delete()
        cli.copycard(cli.cardpath,os.path.join(cli.stdir,self.copyfolder))

    def on_combobox1_changed(self,widget):
        row = widget.get_active_iter()
        if row != None:
            model = widget.get_model()
            self.copyfolder = model[row][0]
            print("Selected: %s" % self.copyfolder)
        else:
            self.copyfolder = widget.get_child().get_text()
            print("Entered: %s" % self.copyfolder)

    ##### No space to copy files message dialog #####

    def on_nospacemessage_response(self,widget,*args):
        widget.hide_on_delete()

class FileChooserDialog(Gtk.Window):
    """File chooser dialog when changing working directory"""
    #coder was too stupid to create a functional fcd with Glade so she borrowed some code from the documentation site
    def on_folder_clicked(self):
        Gtk.Window.__init__(self, title="Change working directory")
        dialog = Gtk.FileChooserDialog("Choose directory", self,
            Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             "Apply", Gtk.ResponseType.OK))
        dialog.set_default_size(800, 400)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print(_("Select clicked"))
            print(_("Folder selected: ") + dialog.get_filename())
            self.selectedfolder = dialog.get_filename()
        elif response == Gtk.ResponseType.CANCEL:
            print(_("Cancel clicked"))
        dialog.destroy()

class GoProGUI:

    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.set_translation_domain(cli.appname)
        self.builder.add_from_file(cli.gladefile)
        self.builder.connect_signals(Handler())

    def get_window_content(self):
        """Fill main window with content"""
        self.show_workdir()
        self.load_dircontent()
        self.find_sd()

        self.builder.get_object("treeview-selection").set_mode(Gtk.SelectionMode.SINGLE)
        
        window = self.builder.get_object("gpwindow")
        window.show_all()

    def show_workdir(self):
        """Show path to working directory"""
        self.builder.get_object("act_wdir").set_text(cli.stdir)

    def load_dircontent(self):
        """Display content of working directory with TreeView"""
        #Tabelle leeren, da sonst bei jeder Aktualisierung Zeilen nur angefügt werden
        self.builder.get_object("treestore1").clear()
        os.chdir(cli.stdir)
        self.get_tree_data(cli.stdir)
        self.builder.get_object("treeview").expand_all()
        self.builder.get_object("treeview-selection").unselect_all()
        #Buttons auf inaktiv setzen, da sonst Buttons entsprechend der letzten parent-Zeile aktiviert werden
        self.activate_tl_buttons(0,0,0,False)

    def get_tree_data(self,directory,parent=None):
        #FIXME: only reads subdirectories not the content of self.stdir itself, which isn't an issue at all when using import function
        for dirs in sorted(os.listdir(directory)):
            path=os.path.join(directory,dirs)
            if os.path.isdir(path):
                os.chdir(dirs)
                #count media
                vidcount = len(glob.glob('*.MP4'))
                imgcount = len(glob.glob('*.JPG'))
                #size of directory, subdiretories exclued
                size = sum([os.path.getsize(f) for f in os.listdir('.') if os.path.isfile(f)])
                humansize = self.sizeof_fmt(size)
                #number of sequences
                try:
                    #4th/5th position in file name of last element in sorted list of sequences (e.g. Seq_03_010.JPG)
                    seq = int(sorted(glob.glob('Seq_*_*.JPG'))[-1][4:6])
                except:
                    seq = 0
                #transmit row to treestore
                row = self.builder.get_object("treestore1").append(parent,[dirs,vidcount,imgcount,humansize,path,seq,False])
                #last column set True if subdirectory contains photo sequences
                if seq != 0:
                    self.builder.get_object("treestore1").set_value(parent,6,True)
                #read subdirs as child rows
                self.get_tree_data(path,row)
                os.chdir("..")

    def activate_tl_buttons(self,v,i,p,s):
        """Buttons only activated if function is available for file(s)"""
        if v>0:
            self.builder.get_object("tlvideo_button").set_sensitive(True)
        else:
            self.builder.get_object("tlvideo_button").set_sensitive(False)
        if i>1:
            self.builder.get_object("tlimage_button").set_sensitive(True)
        else:
            self.builder.get_object("tlimage_button").set_sensitive(False)
        if s is True:
            self.builder.get_object("tlimage_sub_button").set_sensitive(True)
        else:
            self.builder.get_object("tlimage_sub_button").set_sensitive(False)

    def timelapse_vid(self,p,m):
        """Create video timelapse"""
        #p=path, m=multiplier    
        self.reset_progressbar()
        os.chdir(p)
        ctl.makeldir()
        ctl.ffmpeg_vid(p,m)
        self.load_dircontent()

    def timelapse_img(self,p):
        """Create timelapse from images"""
        #p=path
        self.reset_progressbar()
        os.chdir(p)
        ctl.ldir_img(p)
        ctl.ffmpeg_img(p)
        self.load_dircontent()
        
    def timelapse_img_subfolder(self,p):
        """Create timelapse from images in subfolders"""
        self.reset_progressbar()
        os.chdir(p)
        ctl.makeldir()
        abs_subf = len(glob.glob("Images_1*"))
        counter = 0
        for dirs in sorted(os.listdir(p)):
            if dirs.startswith('Images_1'):
                counter += 1
                cli.show_message(_("Create %d of %d") % (counter,abs_subf))
                self.refresh_progressbar(counter,abs_subf)
                ctl.ffmpeg_img(dirs)
                os.chdir('..')
        self.load_dircontent()

    def refresh_progressbar(self,c,a):
        """Progress bar"""
        fraction = c/a
        try:
            self.builder.get_object("progressbar").set_fraction(fraction)
            #see  http://faq.pygtk.org/index.py?req=show&file=faq23.020.htp or http://ubuntuforums.org/showthread.php?t=1056823...it, well, works
            while Gtk.events_pending(): Gtk.main_iteration()
        except:
            pass

    def reset_progressbar(self):
        """Reset progress bar"""
        try:
            self.builder.get_object("progressbar").set_fraction(0.0)
            while Gtk.events_pending(): Gtk.main_iteration()
        except:
            pass

    def find_sd(self):
        cli.detectcard()
        if cli.cardfound is True:
            #activate buttons if card is mounted
            self.builder.get_object("act_sd").set_text(cli.cardpath)
            self.builder.get_object("import_sd").set_sensitive(True)
            self.builder.get_object("open_sd").set_sensitive(True)
        else:
            self.builder.get_object("act_sd").set_text("(none)")
            self.builder.get_object("import_sd").set_sensitive(False)
            self.builder.get_object("open_sd").set_sensitive(False)

    #borrowed from http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    def sizeof_fmt(self,num, suffix='B'):
        """File size shown in common units"""
        for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
            if abs(num) < 1024.0:
                return "%3.1f %s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f %s%s" % (num, 'Yi', suffix)

    def get_targetfolderwindow_content(self):
        """Get list for dropdown selection and open window"""
        copyfolder_list = self.builder.get_object("liststore1")
        copyfolder_list.clear()
        #first row = default folder (today's date)
        today = time.strftime("%Y-%m-%d",time.localtime())
        copyfolder_list.append([today])

        for d in sorted(os.listdir(cli.stdir)):
            if d != today:
                copyfolder_list.append([d])
        
        #bug: no effects when set in glade
        self.builder.get_object("combobox1").set_entry_text_column(0)
        #set first row as default editable entry
        self.builder.get_object("combobox1").set_active(0)

        window = self.builder.get_object("targetfolderwindow")
        window.show_all() 

    def main(self):
        Gtk.main()

class GoProGo:

    def __init__(self):
        
        self.gladefile = os.path.join(os.getcwd(),"herostuff","gopro.glade")
        self.locales_dir = os.path.join(os.getcwd(),'herostuff','po','locale')
        self.appname = 'GPT'

        #setting up localization
        locale.bindtextdomain(self.appname,self.locales_dir)
        locale.textdomain(self.locales_dir)      
        gettext.bindtextdomain(self.appname,self.locales_dir)
        gettext.textdomain(self.appname)
    
        #check for config file to set up working directory
        #create file in case it does not exist
        self.config = os.path.join(os.path.expanduser('~'),".config","gpt.conf")
        self.defaultwdir = os.path.join(os.path.expanduser('~'),"GP")
        
        if os.path.isfile(self.config) is False:
            self.stdir = self.defaultwdir
            self.chkdir(self.stdir)      
            self.createconfig(self.stdir)
        else:
            self.readconfig()
        self.show_message("Working directory: %s" % self.stdir)

    def createconfig(self,wdir):
        """Creates new configuration file and writes current working directory"""

        print("Creating config file...")
        config = open(self.config,"w")
        config.write("""##### CONFIG FILE FOR GOPRO TOOL #####
##### EDIT IF YOU LIKE. YOU ARE AN ADULT. #####

""")
        config.close()
        self.write_wdir_config(wdir)

    def write_wdir_config(self,wdir):
        """Write value for working directory to configuration file"""
        
        config = open(self.config,"a")
        config.write("\n##### working directory #####\nwdir = %s\n" % wdir)
        config.close()

    def replace_wdir_config(self,wdir):
        """Writes new working directory in config file when changed"""
        
        for line in fileinput.input(self.config,inplace=True):
            if line.startswith("wdir"):
                sys.stdout.write("wdir = %s" % wdir)
            else:
                sys.stdout.write(line)

    def readconfig(self):
        """Reads working directory (line begins with "wdir = ...") from configuration file and tries to apply given value. If this attempt fails (due to permission problems) or there is no matching line the default value (~/GP) will be set."""
        
        config = open(self.config,"r")
        match = False
        for line in config:
            if line.startswith("wdir"):
                match = True
                self.stdir = os.path.abspath(line.split("=")[1].strip())
                if self.chkdir(self.stdir) is False:
                    self.stdir = self.defaultwdir
                    self.replace_wdir_config(self.stdir)
                continue
        config.close()
        #add wdir line when not found
        if match is False:
            self.show_message("No configuration for working directory in config file. Set default value (~/GP)...")
            self.stdir = self.defaultwdir
            self.chkdir(self.stdir) 
            #write default wdir to config file
            self.write_wdir_config(self.stdir)

    def show_message(self,message):
        """Show notifications in terminal window and status bar if possible"""
        print(message)
        try:
            app.builder.get_object("statusbar1").push(1,message)
        except:
            pass

    #Arbeitsverzeichnis festlegen
    def chwdir(self):
        """Setting up working directory, default: ~/GP"""
        while 1:
            befehl = input(_("Change working directory? (y/N) "))
            if befehl == "y":
                newdir = input(_("Input path: "))
                if newdir == "":
                    self.show_message(_("No change."))
                    break
                else:
                    self.chkdir(newdir)
                    self.stdir = os.getcwd()
                    self.replace_wdir_config(newdir)
                    break
            elif befehl == "n" or befehl=="":
                self.show_message(_("Everything stays as it is."))
                break
            else:
                self.show_message(_("Invalid input"))

    #function exclusively called by cli
    def handlecard(self):
        self.detectcard()
        if self.cardfound is True:
            while 1:
                befehl = input(_("Memory card found. Copy and rename media files to working directory? (y/n) "))
                if befehl == "n":
                    self.show_message(_("Move along. There is nothing to see here."))
                    break
                elif befehl == "y":
                    if self.freespace(self.cardpath,self.stdir) is True:
                        self.copycard(self.cardpath,os.path.join(self.stdir,self.choosecopydir(self.stdir)))
                        break
                    else:
                        self.show_message(_("Failed to copy files. Not enough free space."))
                        break
                else:
                    self.show_message(_("Invalid input"))

    #Speicherkarte suchen
    def detectcard(self):
        """Find mounted memora card"""
        #works for me on Archlinux, where do other distros mount removable drives? (too lazy for research...)
        #TODO try different paths
        userdrive = os.path.join("/run","media",getpass.getuser())
        self.cardfound = False
        self.show_message(_("Search device in %s") % userdrive)
        try:
            os.chdir(userdrive)
            for d in os.listdir():
                os.chdir(d)
                self.show_message(_("Search in %s") % d)
                if "Get_started_with_GoPro.url" in os.listdir():
                    self.cardfound = True
                    self.cardpath = os.path.join(userdrive,d)
                    return
                else:
                    self.show_message(_("No GoPro device"))
                os.chdir('..')
            #wieder ins ursprüngliche Arbeitsverzeichnis wechseln
            self.workdir(self.stdir)
        except:
            self.show_message(_("No devices found."))

    #Dateien kopieren und umbenennen
    def copycard(self,mountpoint,targetdir):
        """Copy media files to target folder in working directory and rename them"""
        self.chkdir(targetdir)
        print("Copy files from %s to %s." % (mountpoint,targetdir))
        self.copymedia(os.path.join(mountpoint,"DCIM"),targetdir)
        self.show_message(_("Files successfully copied."))
        os.chdir(targetdir)
        for path, dirs, files in os.walk(targetdir):
            os.chdir(path)
            self.sortfiles()
        os.chdir(mountpoint)

    #Speicherplatz analysieren
    def freespace(self,src,dest):
        """Check for free disc space"""
        if shutil.disk_usage(src).used < shutil.disk_usage(dest).free:
            return True
        else:
            return False

    #Zielordner wählen, neuen oder bestehenden Ordner, Defaultwert yyyy-mm-dd
    def choosecopydir(self,wdir):
        os.chdir(wdir)
        #default folder name is today's date
        default = time.strftime("%Y-%m-%d",time.localtime())
        self.copydirlist=[]
        counter = 0
        for d in os.listdir(wdir):
            #get folders in directory without hidden
            if os.path.isdir(d) and not d.startswith("."):
                counter += 1
                self.copydirlist.append([counter,d])
        if counter > 0:
            print("(project) folders in working directory")
            print("**************************************")
            print(_("--> {0:^6} | {1:25}").format(_("no"),_("name")))
            for n in self.copydirlist:
                print(_("--> {0:^6} | {1:25}").format(n[0],n[1]))
        else:
            print("There are no subfolders in the working directory yet")
        return self.copydir_prompt(default,counter)

    def copydir_prompt(self,default,c):
        """Value returned is name of default or selected subfolder"""
        if c == 0:
            return default
        while 1:
            try:
                prompt = input(_("Select directory to copy file to (return for default value: %s): ") % default)
                if prompt == "":
                    return default
                elif int(prompt) > c or int(prompt) < 1:
                    print(_("Invalid input, input must be integer between 1 and %d. Try again...") % c)
                else:
                    return self.copydirlist[int(prompt)-1][1]
            except ValueError:
                print(_("Invalid input (integer required). Try again..."))

    #Medien kopieren
    def copymedia(self,src,dest):
        """Copy files from card to working directory (preview files excluded)"""
        os.chdir(src)
        for d in os.listdir():
            os.chdir(d)
            self.show_message(d)
            if glob.glob('*.JPG'):
                self.show_message(_("Found photos"))
                #for easy handling keep pictures in subfolders analogue to source file structure
                self.chkdir(os.path.join(dest,"Images_"+d[0:3]))
                self.workdir(os.path.join(src,d))
            #counter for progress bar
            counter = 0
            abs_files = len(os.listdir())
            app.reset_progressbar()
            for f in os.listdir():
                if f.endswith(".MP4"):
                    if os.path.exists(os.path.join(dest,f)):
                        self.show_message(_("%s already exists in target directory") % f)
                    else:
                        self.show_message(_("Copy %s") % f)
                        shutil.copy(f,dest)
                if f.endswith(".JPG"):
                    if os.path.exists(os.path.join(dest,"Images_"+d[0:3],f)):
                        self.show_message(_("%s already exists in target directory") % f)
                    else:
                        self.show_message(_("Copy %s") % f)
                        shutil.copy(f,os.path.join(dest,"Images_"+d[0:3]))
                counter += 1
                app.refresh_progressbar(counter,abs_files)
            os.chdir('..')

    #Verzeichnisse anlegen, wenn möglich, falls nicht, Fallback in vorheriges Arbeitsverzeichnis
    #Gebrauch: Initialisierung/Änderung des Arbeitsverzeichnisses, Erstellung von Unterordnern vor Kopieren der Speicherkarte (Abfrage, um eventuelle Fehlermeldung wegen bereits vorhandenen Ordners zu vermeiden)
    def chkdir(self,path):
        """Create folder if nonexistent, check for write permission then change into directory"""
        try:
            os.makedirs(path)
            print(_("Folder created."))
            self.workdir(path)
        except OSError as exception:
            if exception.errno == errno.EEXIST:
                print(_("Directory already exists. OK."))
                if os.access(path,os.W_OK):
                    self.workdir(path)
                else:
                    self.show_message(_("Error: no write permission"))
                    self.workdir(self.stdir)
            elif exception.errno == errno.EACCES:
                print("Permission denied.")
                return False
            else:
                self.show_message(_("Invalid path"))
                self.workdir(self.stdir)
            

    #Verzeichnis wechseln
    def workdir(self,path):
        """Change directory"""
        self.show_message(_("Change directory to %s") % path)
        os.chdir(path)

    def sortfiles(self):
        """Save video files in (chrono)logical order. Photos are seperated by single shots and sequences. FFmpeg explicitly requires file numbering in "%d" format for timelapse creation. GoPro saves a maximum of 999 files per subfolder so 001.JPG..00n.JPG is sufficient"""
        #Video
        if glob.glob('GP*.MP4') or glob.glob('GOPR*.MP4'):
            message = "%d video file(s) will be renamed." % (len(glob.glob('GP*.MP4'))+len(glob.glob('GOPR*.MP4')))
            self.show_message(message)
            for f in glob.glob('GP*.MP4'):
                newfile=f[4:8]+f[2:4]+".MP4"
                self.show_message(_("Rename %s to %s.") % (f,newfile))
                os.rename(f,newfile)
            for f in glob.glob('GOPR*.MP4'):
                newfile=f[4:8]+"00.MP4"
                self.show_message(_("Rename %s to %s.") % (f,newfile))
                os.rename(f,newfile)
        else:
            if glob.glob('*.MP4') or glob.glob('*.mp4'):
                self.show_message(_("Video files do not match the GoPro naming convention. No need for renaming or renaming already done."))
            else:
                self.show_message(_("No video files."))
        #Foto
        #Sequenzen nummeriert nach Muster Seq_0n_00n.JPG, Einzelfotos Img_00n.JPG
        if glob.glob('G0*.JPG') or glob.glob('GOPR*.JPG'):
            #Einzelbilder
            message = "%d image files will be renamed." % (len(glob.glob('G*.JPG'))+len(glob.glob('GOPR*.JPG')))
            self.show_message(message)
            counter=1
            for f in sorted(glob.glob('GOPR*.JPG')):
                newfile="Img_%03d.JPG" % (counter)
                self.show_message(_("Rename %s to %s.") % (f,newfile))
                os.rename(f,newfile)
                counter+=1
            #counter for files
            counter=1
            #sequence number can be extracted from file name
            seq=sorted(os.listdir())[0][2:4]
            for f in sorted(glob.glob('G0*.JPG')):
                if f[2:4] == seq:
                    newfile="Seq_"+seq+"_%03d.JPG" % (counter)
                else:
                    counter=1
                    seq=f[2:4]
                    newfile="Seq_"+seq+"_%03d.JPG" % (counter)
                self.show_message(_("Rename %s to %s.") % (f,newfile))
                os.rename(f,newfile)
                counter+=1
        else:
            if glob.glob('*.JPG'):
                self.show_message(_("Image files do not match the GoPro naming convention. No need for renaming or renaming already done."))
            else:
                #andere Formate etc.
                self.show_message(_("No matching image files."))
        #Vorschaudateien
        #FIXME: obsolet, da nur relevante Dateien kopiert werden, trotzdem erstmal lassen
        #Featureidee: Vorschaufenster mit Info zu Medien (Auflösung, FPS...)
        if glob.glob('*.LRV') or glob.glob('*.THM'):
            print(len(glob.glob('*.LRV'))+len(glob.glob('*.THM')),_("preview file(s) (LRV/THM) found."))
            self.delfiles(".LRV",".THM")
        app.reset_progressbar()

    #Dateien löschen, obsolet, siehe Vorschaudateien
    def delfiles(self,ftype):
        """Dateien bestimmten Typs löschen"""
        while 1:
            print()
            befehl=input(_("Delete (y/n) "))
            if befehl == "y":
                for file in os.listdir(self.dir):
                    if file.endswith(ftype):
                        self.show_message(_("Deleting %s.") % file)
                        os.remove(file)
                break
            elif befehl == "n":
                break
            else:
                self.show_message(_("Invalid input. Try again..."))

    #Menü
    def help(self):
        """Serving the menu..."""
        print(_("""
        (h)elp
        
        ------- routines ----
        change (w)orking directory
        detect (c)ard
        (r)ead directory and rename GoPro files

        ------- create ------
        timelapse from (v)ideo
        timelapse from (i)mages

        (q)uit"""))

    def shell(self):
        """Input prompt"""
        while 1:
            print()
            befehl = input()
            if befehl == 'h' or befehl == '':
                self.help()
            elif befehl == 'r':
                self.sortfiles()
            elif befehl == 'c':
                self.handlecard()
            elif befehl == 'w':
                self.chwdir()
            elif befehl == 'v':
                ctl.countvid()
            elif befehl == 'i':
                ctl.countimg()
            elif befehl == 'q':
                break
            else:
                print(_("Invalid input. Try again..."))

class TimeLapse:

    def __init__(self):
        self.wdir= os.getcwd()
        
    def makeldir(self):
        """Create folder for timelapses"""
        try:
            os.makedirs("lapse")
            cli.show_message(_("Folder created."))
        except:
            cli.show_message(_("Folder already exists. OK."))
        self.ldir = os.path.join(self.wdir,"lapse")

    def countvid(self):
        """Find video files in directory"""
        self.wherevid=[]
        counter=0
        for path,dirs,files in sorted(os.walk(self.wdir)):
            os.chdir(path)
            if len(glob.glob('*.MP4')) > 0:
                counter+=1
                self.wherevid.append([counter,path,len(glob.glob('*.MP4'))])
        if counter>0:
            print(_("""
Video:
******"""))
            print(_("--> {0:^6} | {1:40} | {2:>}".format("No.","Directory","Amount")))
            for n in self.wherevid:
                print(_("--> {0:^6} | {1:40} | {2:>4}").format(n[0],n[1],n[2]))
            self.choosevid(counter)
        else:
            print(_("No video files found."))

    def choosevid(self,c):
        """Create timelapse video for all video files in selected folder"""
        while 1:
            try:
                befehl = int(input(_("Select directory to create timelapse video of (0 to cancel): ")))
                if befehl == 0:
                    break
                elif befehl > c or befehl < 0:
                    print(_("Invalid input, input must be integer between 1 and",c,". Try again..."))
                else:
                    message = "Create timelapse for directory "+self.wherevid[befehl-1][1]
                    cli.show_message(message)
                    self.choosemult(self.wherevid[befehl-1][1])
                    break
            except ValueError:
                print(_("Invalid input (no integer). Try again..."))

    def choosemult(self,path):
        """Specify multiplier for timelapse video."""
        os.chdir(path)
        self.makeldir()
        while 1:
            try:
                mult = float(input(_("Multiplier: ")))
                if mult == 0:
                    break
                elif mult <= 1:
                    print(_("Multiplier must be larger than 1."))
                else:
                    self.ffmpeg_vid(path,mult)
                    break
            except ValueError:
                print(_("Invalid input (no number). Try again..."))

    def ffmpeg_vid(self,path,m):
        """Let FFmpeg compute timelapse"""
        os.chdir(path)
        #counter for progress bar
        counter=0
        abs_vid = len(glob.glob('*MP4'))
        for f in glob.glob('*.MP4'):
            counter+=1
            cli.show_message(_("Create %d of %d") % (counter,abs_vid))
            #converted from bash script
            #ffmpeg -i $file -r 30 -filter:v "setpts=1/$1*PTS" -an lapse/${file:0:-4}-x$1.MP4
            filename=os.path.join("lapse",f[0:-4]+"-x"+str(m)+".MP4")
            speed = "setpts=1/"+str(m)+"*PTS"
            command = ['ffmpeg',
                        '-y',
                        '-i', f,
                        '-r', '30',
                        '-filter:v', speed,
                        '-an',
                        '-nostats',
                        '-loglevel', '0',
                        filename]
            subprocess.run(command)
            app.refresh_progressbar(counter,abs_vid)
        cli.show_message(_("Done."))

    def countimg(self):
        """Find image files in directory"""
        self.whereimg=[]
        counter=0
        for path,dirs,files in sorted(os.walk(self.wdir)):
            os.chdir(path)
            if len(glob.glob('*.JPG')) > 0:
                counter+=1
                self.whereimg.append([counter,path,len(glob.glob('*.JPG'))])
        if counter>0:
            print(_("""
Images:
*******"""))
            print(_("--> {0:^6} | {1:40} | {2:>}".format("No.","Directory","Amount")))
            for n in self.whereimg:
                print(_("--> {0:^6} | {1:40} | {2:>4}").format(n[0],n[1],n[2]))
            self.chooseimg(counter)
        else:
            print(_("No photos found."))

    #TODO: merge with choosevid, almost identical
    def chooseimg(self,c):
        """Create timelapse video(s) for all image files in selected directory"""
        while 1:
            try:
                befehl = int(input(_("Select directory to create timelapse video of (0 to cancel): ")))
                if befehl == 0:
                    break
                elif befehl > c or befehl < 0:
                    print(_("Invalid input, input must be integer between 1 and",c,". Try again..."))
                else:
                    print(_("Create timelapse for directory "),self.whereimg[befehl-1][1])
                    self.ldir_img(self.whereimg[befehl-1][1])
                    self.ffmpeg_img(self.whereimg[befehl-1][1])
                    break
            except ValueError:
                print(_("Invalid input (no integer). Try again..."))

    def ldir_img(self,path):
        """Create timelapse folder for photo timelapses"""
        os.chdir(path)
        #Bei Foto-Timelapses ein Verzeichnis darüber speichern, da ansonsten immer extra lapse-Verzeichnis mit einem Video darin erstellt wird, einfach, aber unelegant...
        os.chdir("..")
        self.makeldir()
        os.chdir(path)

    def ffmpeg_img(self,path):
        """Let FFmpeg compute a timelapse per sequence with 30 fps and original resolution"""
        #30 fps works for me because I choose a suitable interval depending on record length and purpose. Here I just want this kind of 'raw' video which needs additional cropping to fit into widescreen format and probably some color enhancement, background music etc. so a video editing program is mandatory anyway.
        os.chdir(path)
        seq = int(sorted(glob.glob('Seq_*_*.JPG'))[-1][4:6])
        for s in range(1,seq+1):
            cli.show_message(_("Create %d of %d") % (s,seq))
            #converted from bash script
            #ffmpeg -f image2 -r 30 -i %04d.jpg -r 30 ../lapse/$dir.MP4
            f = "Seq_%02d_" % (s) + "%03d.JPG"
            filename = os.path.join("..","lapse","Seq_%02d_%s.MP4" % (s,path[-2:]))
            command = ['ffmpeg',
                        '-y',
                        '-f', 'image2',
                        '-r', '30',
                        '-i', f,
                        '-r', '30',
                        '-nostats',
                        '-loglevel', '0',
                        filename]
            subprocess.run(command)
        cli.show_message(_("Done."))

cli = GoProGo()
ctl = TimeLapse()
app = GoProGUI()
