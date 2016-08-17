#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import errno
import glob
import getpass
import time
import shutil
import subprocess
import fileinput
import locale
import gettext
import threading
import sys
import codecs

#requires python-lxml
from lxml import etree

_ = gettext.gettext

try:
    import gi
    gi.require_version('Gtk','3.0')
    from gi.repository import Gtk,Gdk
except:
    print(_("Could not load GTK+, only command-line version is available."))
    raise

class Handler:
    """Signal assignment for Glade"""

    ##### close button for all except main application window #####
    
    def on_window_delete_event(self,widget,event):

        #hide_on_delete prevents window from being destroyed so it can be retrieved
        widget.hide_on_delete()

        #The 'return True' part indicates that the default handler is _not_ to be called, and therefore the window will not be destroyed.
        #see http://faq.pygtk.org/index.py?req=edit&file=faq10.006.htp
        return True

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
        app.discspace_info()

    def on_open_wdir_clicked(self,widget):
        subprocess.run(['xdg-open',cli.stdir])

    #right toolbar (memory card)
    def on_import_sd_clicked(self,widget):
        app.get_targetfolderwindow_content()
        #if cli.freespace(cli.cardpath,cli.stdir) is True:
        #    app.get_targetfolderwindow_content()
        #else:
            #cli.show_message(_("Failed to copy files. Not enough free space."))
            #app.builder.get_object("nospacemessage").run()
            

    def on_find_sd_clicked(self,widget):
        #delete sd content info and no space info
        app.builder.get_object("sd_content_info").set_text("")
        app.builder.get_object("nospace_info").set_text("")
        app.find_sd()
        app.discspace_info()

    def on_open_sd_clicked(self,widget):
        subprocess.run(['xdg-open',cli.cardpath])

    def on_format_sd_clicked(self,widget):
        app.builder.get_object("confirm_format_dialog").show_all()

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
            #absolute path stored in 5th column in treestore, not displayed in treeview
            self.sel_folder = row[pos][4]
            #number of video files
            self.sel_vid = row[pos][1]
            app.activate_tl_buttons(row[pos][1],row[pos][2],row[pos][4],row[pos][6])

    #calculate timelapse
    def on_tlvideo_button_clicked(self,widget):
        app.builder.get_object("multwindow").show_all()
        
    def on_tlimage_button_clicked(self,widget):
        app.timelapse_img(self.sel_folder)

    def on_tlimage_sub_button_clicked(self,widget):
        app.timelapse_img_subfolder(self.sel_folder)

    #right click menu in treeview
    def on_treeview_button_release_event(self,widget,event):
        #define context menu
        popup=Gtk.Menu()
        kd_item=Gtk.MenuItem(_("Open with Kdenlive"))
        #selected row is already caught by on_treeview_selection_changed function
        kd_item.connect("activate",self.on_open_with_kdenlive,self.sel_folder)
        
        #don't show menu item if there are no video files
        if self.sel_vid > 0 and cli.kd_supp is True:
            popup.append(kd_item)

        open_item=Gtk.MenuItem(_("Open folder"))
        open_item.connect("activate",self.on_open_folder,self.sel_folder)
        popup.append(open_item)
        popup.show_all()
        #only show on right click
        if event.button == 3:
            popup.popup(None,None,None,None,event.button,event.time)
            return True

    def on_open_with_kdenlive(self,widget,folder):
        kds.create_project(folder)

    def on_open_folder(self,widget,folder):
        subprocess.run(['xdg-open',folder])

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
        #TODO add cancel button to kill import job
        app.builder.get_object("targetfolderwindow").hide_on_delete()
        app.builder.get_object("importmessage").show_all()
        time.sleep(.1)
        cli.copycard(cli.cardpath,os.path.join(cli.stdir,self.copyfolder))
        app.builder.get_object("importmessage").hide_on_delete()
        app.load_dircontent()
        app.discspace_info()

    def on_combobox1_changed(self,widget):
        row = widget.get_active_iter()
        if row != None:
            model = widget.get_model()
            self.copyfolder = model[row][0]
            cli.show_message(_("Selected: %s") % self.copyfolder)
        else:
            self.copyfolder = widget.get_child().get_text()
            cli.show_message(_("Entered: %s") % self.copyfolder)

    ##### No space to copy files message dialog #####

    def on_nospacemessage_response(self,widget,*args):
        widget.hide_on_delete()

    ##### About dialog #####
    
    def on_ok_about_clicked(self,widget):
        app.builder.get_object("aboutdialog").hide_on_delete()

    ##### Menu #####

    def on_menu_about_activate(self,widget):
        app.builder.get_object("aboutdialog").show()

    def on_tl_calc_activate(self,widget):
        app.builder.get_object("tl_calc_win").show()

    def on_menu_kd_support_toggled(self,widget):
        cli.kd_supp = widget.get_active()
        cli.change_kd_support_config(cli.kd_supp)

    ##### Timelapse calculator window #####

    def on_spin_hours_value_changed(self,widget):
        tlc.dur_hours = tlc.get_spinbutton_data(widget)
        tlc.set_fileinfo()

    def on_spin_minutes_value_changed(self,widget):
        tlc.dur_min = tlc.get_spinbutton_data(widget)
        tlc.set_fileinfo()

    def on_spin_fps_value_changed(self,widget):
        tlc.fps = tlc.get_spinbutton_data(widget)
        tlc.set_fileinfo()

    def on_combobox_res_changed(self,widget):
        tlc.fsize = tlc.get_combobox_data(widget,2)
        tlc.set_fileinfo()      

    def on_combobox_intvl_changed(self,widget):
        tlc.intvl = tlc.get_combobox_data(widget,1)
        tlc.set_fileinfo()

    ##### Confirm formating SD card #####
    
    def on_confirm_format_dialog_response(self,widget,event):
        widget.hide_on_delete()
        if event == -5:
            cli.format_sd()
            app.find_sd()
            app.discspace_info()
            
class FileChooserDialog(Gtk.Window):
    """File chooser dialog when changing working directory"""
    #coder was too stupid to create a functional fcd with Glade so she borrowed some code from the documentation site
    def on_folder_clicked(self):
        Gtk.Window.__init__(self, title=_("Change working directory"))
        dialog = Gtk.FileChooserDialog(_("Choose directory"), self,
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
        
        #load glade files
        for f in cli.gladefile:
            self.builder.add_from_file(f)

    def get_window_content(self):
        """Fill main window with content"""
        
        self.show_workdir()
        self.load_dircontent()
        self.find_sd()
        self.discspace_info()

        #only one treeview row can be selected
        self.builder.get_object("treeview-selection").set_mode(Gtk.SelectionMode.SINGLE)

        #set Kdenlive support menu item inactive when disabled
        if cli.kd_supp is False:
            self.builder.get_object("menu_kd_support").set_active(False)

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
                #write number of sequences into table for future use
                #TODO show number of seqs in treeview
                try:
                    #4th/5th position in file name of last element in sorted list of sequences (e.g. Seq_03_010.JPG)
                    seq = int(sorted(glob.glob('Seq_*_*.*'))[-1][4:6])
                except:
                    seq = 0
                #transmit row to treestore
                row = self.builder.get_object("treestore1").append(parent,[dirs,vidcount,imgcount,humansize,path,seq,False])
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
        self.refresh_progressbar(0,1)
        os.chdir(p)
        ctl.makeldir()
        ctl.ffmpeg_vid(p,m)
        self.load_dircontent()

    def timelapse_img(self,p):
        """Create timelapse from images"""
        #p=path
        self.refresh_progressbar(0,1)
        os.chdir(p)
        ctl.ldir_img(p)
        ctl.ffmpeg_img(p)
        self.load_dircontent()
        
    def timelapse_img_subfolder(self,p):
        """Create timelapse from images in subfolders"""
        self.refresh_progressbar(0,1)
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
        """Refresh progress bar with current status"""
        fraction = c/a
        try:
            self.builder.get_object("progressbar").set_fraction(fraction)
            time.sleep(.1)
            #see  http://faq.pygtk.org/index.py?req=show&file=faq23.020.htp or http://ubuntuforums.org/showthread.php?t=1056823...it, well, works
            while Gtk.events_pending(): Gtk.main_iteration()
        except:
            pass

    def find_sd(self):
        if cli.detectcard() is True:
            #activate buttons if card is mounted
            self.builder.get_object("act_sd").set_text(cli.cardpath)
            self.builder.get_object("open_sd").set_sensitive(True)
            self.builder.get_object("format_sd").set_sensitive(True)
            self.builder.get_object("sd_content_info").set_text(cli.card_content(cli.cardpath))
            if cli.freespace(cli.cardpath,cli.stdir) is True:
                self.builder.get_object("import_sd").set_sensitive(True)
            else:
                self.builder.get_object("import_sd").set_sensitive(False)
                self.builder.get_object("nospace_info").set_text("Not enough disc space.\nFree at least %s." % cli.needspace)
        else:
            self.builder.get_object("act_sd").set_text(_("(none)"))
            self.builder.get_object("import_sd").set_sensitive(False)
            self.builder.get_object("open_sd").set_sensitive(False)
            self.builder.get_object("format_sd").set_sensitive(False)

    def discspace_info(self):
        """Save memory information about disc and card in list [total,used,free], use values to display levelbar and label element below"""
        
        self.disc_space = [shutil.disk_usage(cli.stdir).total,
                            shutil.disk_usage(cli.stdir).used,
                            shutil.disk_usage(cli.stdir).free]
        if cli.detectcard() is True:
            self.card_space = [shutil.disk_usage(cli.cardpath).total,
                                shutil.disk_usage(cli.cardpath).used,
                                shutil.disk_usage(cli.cardpath).free,True]
        else:
            self.card_space = [1,0,0,False]

        self.disc_bar = self.builder.get_object("level_wdir")
        self.card_bar = self.builder.get_object("level_sd")

        css = b"""
        
levelbar trough block.filled.empty {
    border-color: transparent;
    background-color: transparent;
    }

levelbar trough block.filled {
    background-color: #FF0000;
}

levelbar trough block.filled.lower {
    background-color: #00D30F;
}

levelbar trough block.filled.low {
    background-color: #0000FF;
}

levelbar trough block.filled.high {
    background-color: #FF4D00;
}
        """

        #load css stylesheet
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        self.disc_bar.add_offset_value("lower",0.5)
        self.disc_bar.add_offset_value("low",0.7)
        self.disc_bar.add_offset_value("high",0.9)

        self.card_bar.add_offset_value("lower",0.4)
        self.card_bar.add_offset_value("low",0.7)
        self.card_bar.add_offset_value("high",0.9)

        self.disc_bar.set_value(self.disc_space[1]/self.disc_space[0])
        self.card_bar.set_value(self.card_space[1]/self.card_space[0])

        self.builder.get_object("free_wdir").set_text(_("free: {0} of {1}").format(self.sizeof_fmt(self.disc_space[2]),self.sizeof_fmt(self.disc_space[0])))
        if self.card_space[3] is True:
            self.builder.get_object("free_sd").set_text(_("free: {0} of {1}").format(self.sizeof_fmt(self.card_space[2]),self.sizeof_fmt(self.card_space[0])))
        else:
            self.builder.get_object("free_sd").set_text("")

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
        
        #glade bug: no effects when set in glade
        self.builder.get_object("combobox1").set_entry_text_column(0)
        #set first row as default editable entry
        self.builder.get_object("combobox1").set_active(0)

        window = self.builder.get_object("targetfolderwindow")
        window.show_all() 

    def main(self):
        Gtk.main()

class GoProGo:

    def __init__(self):

        self.install_dir = os.getcwd()

        #Glade files/window configuration
        gladefile_list = ["gopro.glade","tlcalculator.glade"]
        self.gladefile = []

        for f in gladefile_list:
            self.gladefile.append(os.path.join(self.install_dir,"herostuff",f))

        self.locales_dir = os.path.join(self.install_dir,'herostuff','po','locale')
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
            self.kd_supp = True
        else:
            self.readconfig()
        self.show_message(_("Working directory: %s") % self.stdir)
        
    def createconfig(self,wdir):
        """Creates new configuration file and writes current working directory"""

        print(_("Creating config file..."))
        config = open(self.config,"w")
        config.write(_("""##### CONFIG FILE FOR GOPRO TOOL #####
##### EDIT IF YOU LIKE. YOU ARE AN ADULT. #####
"""))
        config.close()
        self.write_wdir_config(wdir)
        self.write_kd_supp_config()

    def write_wdir_config(self,wdir):
        """Write value for working directory to configuration file"""
        
        config = open(self.config,"a")
        config.write("\n##### working directory #####\nwdir = %s\n" % wdir)
        config.close()

    def write_kd_supp_config(self):
        """Default Kdenlive support is enabled"""

        config = open(self.config,"a")
        config.write("\n##### Kdenlive support #####\nkdsupp = True\n")
        config.close()

    def replace_wdir_config(self,wdir):
        """Writes new working directory in config file when changed"""
        
        for line in fileinput.input(self.config,inplace=True):
            if line.startswith("wdir"):
                sys.stdout.write("wdir = %s\n" % wdir)
            else:
                sys.stdout.write(line)

    def change_kd_support_config(self,supp):
        """Changes Kdenlive support in config file when changed (menu item toggled)"""
        
        for line in fileinput.input(self.config,inplace=True):
            if line.startswith("kdsupp"):
                sys.stdout.write("kdsupp = %s" % supp)
            else:
                sys.stdout.write(line)

    def readconfig(self):
        """Reads working directory and Kdenlive support status (line begins with "wdir = ...") from configuration file and tries to apply given value. If this attempt fails (due to permission problems) or there is no matching line the default value (~/GP) will be set."""
        
        config = open(self.config,"r")
        match_wdir = False
        match_kd = False
        for line in config:
            if line.startswith("wdir"):
                match_wdir = True
                self.stdir = os.path.abspath(line.split("=")[1].strip())
                if self.chkdir(self.stdir) is False:
                    self.stdir = self.defaultwdir
                    self.replace_wdir_config(self.stdir)
                continue
            if line.startswith("kdsupp"):
                if line.split("=")[1].strip() == "True":
                    self.kd_supp = True
                    match_kd = True
                elif line.split("=")[1].strip() == "False":
                    self.kd_supp = False
                    match_kd = True
                else:
                    self.change_kd_support_config(True)
                    self.kd_supp = True
                    match_kd = True
                continue

        config.close()
        #add wdir line when not found
        if match_wdir is False:
            self.show_message(_("No configuration for working directory in config file. Set default value (~/GP)..."))
            self.stdir = self.defaultwdir
            self.chkdir(self.stdir) 
            #write default wdir to config file
            self.write_wdir_config(self.stdir)
        
        if match_kd is False:
            self.show_message(_("Kdenlive support is enabled."))
            self.kd_supp = True
            self.write_kd_supp_config()

    def show_message(self,message):
        """Show notifications in terminal window and status bar if possible"""
        try:
            app.builder.get_object("statusbar1").push(1,message)
            time.sleep(.1)
            while Gtk.events_pending(): Gtk.main_iteration()
        except NameError:
            pass
        print(message)

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
        if self.detectcard() is True:
            self.card_content(self.cardpath)
            while 1:
                befehl = input(_("Memory card found. Copy and rename media files to working directory? (y/n) "))
                if befehl == "n":
                    print(_("Move along. There is nothing to see here."))
                    break
                elif befehl == "y":
                    if self.freespace(self.cardpath,self.stdir) is True:
                        self.copycard(self.cardpath,os.path.join(self.stdir,self.choosecopydir(self.stdir)))
                        break
                    else:
                        print(_("Failed to copy files. Not enough free space."))
                        break
                else:
                    print(_("Invalid input"))

    #Speicherkarte suchen
    def detectcard(self):
        """Find mounted memory card"""
        #works for me on Archlinux, where do other distros mount removable drives? (too lazy for research...)
        #TODO try different paths
        userdrive = os.path.join("/run","media",getpass.getuser())
        self.show_message(_("Search device in %s") % userdrive)
        try:
            os.chdir(userdrive)
            for d in os.listdir():
                os.chdir(d)
                self.show_message(_("Search in %s") % d)
                if "Get_started_with_GoPro.url" in os.listdir():
                    self.subpath_card = "DCIM"
                    self.cardpath = os.path.join(userdrive,d)
                    cli.show_message(_("Found GoPro device."))
                    return True
                elif "SONYCARD.IND" in os.listdir(os.path.join(os.getcwd(),"PRIVATE","SONY")):
                    self.subpath_card = "MP_ROOT"
                    self.cardpath = os.path.join(userdrive,d)
                    cli.show_message(_("Found Sony device."))
                    return True
                else:
                    self.show_message(_("No supported device found."))
                os.chdir('..')
            #wieder ins ursprüngliche Arbeitsverzeichnis wechseln
            self.workdir(self.stdir)
        except:
            self.show_message(_("No devices found."))
            return False

    #collect content information of plugged memory card
    def card_content(self,path):
        print("Card mount point:",path)
        #search for files
        vid_count = 0
        img_count = 0
        vid_size = 0
        img_size = 0
        for root,dirs,files in os.walk(path):
            for filename in files:
                if filename.endswith(".MP4"):
                    vid_count += 1
                    vid_size += os.path.getsize(os.path.join(root,filename))
                elif filename.endswith(".JPG"):
                    img_count += 1
                    img_size += os.path.getsize(os.path.join(root,filename))

        info = "Number of videos: %d, total size: %s\nNumber of images: %d, total size: %s" % (vid_count,app.sizeof_fmt(vid_size),img_count,app.sizeof_fmt(img_size))
        print(info)
        return info

    #Dateien kopieren und umbenennen
    def copycard(self,mountpoint,targetdir):
        """Copy media files to target folder in working directory and rename them"""
        self.chkdir(targetdir)
        self.show_message(_("Copy files from %s to %s.") % (mountpoint,targetdir))
        self.copymedia(os.path.join(mountpoint,self.subpath_card),targetdir)
        self.show_message(_("Files successfully copied."))
        os.chdir(targetdir)
        for path, dirs, files in os.walk(targetdir):
            os.chdir(path)
            self.sortfiles()
        self.show_message(_("Done."))
        os.chdir(mountpoint)

    #Speicherplatz analysieren
    def freespace(self,src,dest):
        """Check for free disc space"""
        if shutil.disk_usage(src).used < shutil.disk_usage(dest).free:
            return True
        else:
            self.needspace = app.sizeof_fmt(shutil.disk_usage(src).used - shutil.disk_usage(dest).free)
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
            print(_("(project) folders in working directory"))
            print(_("**************************************"))
            print("--> {0:^6} | {1:25}".format(_("no."),_("name")))
            for n in self.copydirlist:
                print("--> {0:^6} | {1:25}".format(n[0],n[1]))
        else:
            print(_("There are no subfolders in the working directory yet"))
        return self.copydir_prompt(default,counter)

    def copydir_prompt(self,default,c):
        """Value returned is name of default or selected subfolder"""
        if c == 0:
            return default
        while 1:
            try:
                prompt = input(_("Choose destination folder (return for default value: %s): ") % default)
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
            self.show_message(_("Changed directory to %s") % d)
            time.sleep(.1)

            #for easy handling keep pictures in subfolders analogue to source file structure
            #create subfolder for image sequences
            if glob.glob('*.JPG'):
                self.show_message(_("Found photos..."))
                self.chkdir(os.path.join(dest,"Images_"+d[0:3]))
                self.workdir(os.path.join(src,d))

            #counter for progress bar
            counter = 0
            thread_list = []
            #TODO abf files for images = len(all_image_folders...)
            abs_files = len(os.listdir())

            #reset progressbar
            app.refresh_progressbar(0,1)
            
            #TODO progressbar, wenn thread fertig, ...copied in message tray
            #copy files
            
            #TODO: seperate image/video, image without threading
            for f in sorted(os.listdir()):
                #image files
                if f.endswith(".JPG"):
                    if os.path.exists(os.path.join(dest,"Images_"+d[0:3],f)):
                        #TODO no use because files will be renamed anyways after copying
                        self.show_message(_("%s already exists in target directory.") % f)
                    else:
                        self.show_message(_("Copy %s...") % f)
                        shutil.copy(f,os.path.join(dest,"Images_"+d[0:3]))

                #video files
                if f.endswith(".MP4"):
                    #give the app time to update status and progressbar to avoid delay
                    #time.sleep(1)
                    self.show_message(_("Copy %s...") % f)
                    t = threading.Thread(target=self.copyvid_thread,args=(f,dest,abs_files,))
                    thread_list.append(t)
                    thread_list[-1].start()
                    time.sleep(10)
                        
                counter += 1
                #app.refresh_progressbar(counter,abs_files)

##### copy #####
            #for f in sorted(os.listdir()):
                ##image files
                #if f.endswith(".JPG"):
                    #if os.path.exists(os.path.join(dest,"Images_"+d[0:3],f)):
                        ##TODO no use because files will be renamed anyways after copying
                        #self.show_message(_("%s already exists in target directory.") % f)
                    #else:
                        #self.show_message(_("Copy %s...") % f)
                        #shutil.copy(f,os.path.join(dest,"Images_"+d[0:3]))

                ##video files
                #if f.endswith(".MP4"):
                    #if os.path.exists(os.path.join(dest,f)):
                        ##TODO no use because files will be renamed anyways after copying
                        #self.show_message(_("%s already exists in target directory.") % f)
                        ##give the app time to update status and progressbar to avoid delay
                        #time.sleep(1)
                    #else:
                        #self.show_message(_("Copy %s...") % f)
                        #t = threading.Thread(target=self.copyvid_thread,args=(f,dest,abs_files,))
                        #thread_list.append(t)
                        #thread_list[-1].start()
                        #time.sleep(10)
                        
                #counter += 1
                #app.refresh_progressbar(counter,abs_files)
######################

            if thread_list != []:
                #wait until all threads are finished
                for thread in thread_list:
                    thread.join()
                
            self.show_message(_("Copying files finished."))
            os.chdir('..')

    def copyvid_thread(self,f,dest,abs_files):
        #TODO extra Test mit thread count
        shutil.copy(f,dest)
        print(_("%s copied") % f)
        app.refresh_progressbar(threading.active_count()-1,abs_files)

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
                print(_("Permission denied."))
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
                newfile="gp"+f[4:8]+f[2:4]+".MP4"
                os.rename(f,newfile)
            for f in glob.glob('GOPR*.MP4'):
                newfile="gp"+f[4:8]+"00.MP4"
                os.rename(f,newfile)
        else:
            if glob.glob('*.MP4') or glob.glob('*.mp4'):
                self.show_message(_("Video files do not match the GoPro naming convention. No need for renaming or renaming already done."))
            else:
                self.show_message(_("No video files."))

        #detect existing sequences
        #TODO use treeview seq column instead
        if glob.glob('Seq_*.MP4') == []:
            seq = 0
        else:
            seq = int(sorted(glob.glob('Seq_*.MP4'))[-1][4:6])

        #save in sequences (see image section below), pattern: Seq_0n_0n.MP4
        for f in sorted(glob.glob('gp*.MP4')):
            if f.endswith('00.MP4'):
                seq += 1
            newfile = "Seq_{0:02d}_{1}.MP4".format(seq,f[6:8])
            os.rename(f,newfile)

        #Foto
        #pattern for sequences: Seq_0n_00n.JPG, single shots: Img_00n.JPG
        if glob.glob('G0*.JPG') or glob.glob('GOPR*.JPG'):
            #Einzelbilder
            message = _("%d image files will be renamed.") % (len(glob.glob('G*.JPG'))+len(glob.glob('GOPR*.JPG')))
            self.show_message(message)
            counter=1
            for f in sorted(glob.glob('GOPR*.JPG')):
                newfile="Img_%03d.JPG" % (counter)
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
        if glob.glob('*.LRV') or glob.glob('*.THM'):
            print(len(glob.glob('*.LRV'))+len(glob.glob('*.THM')),_("Preview file(s) (LRV/THM) found."))
            self.delfiles(".LRV",".THM")

    def confirm_format(self):
        if self.detectcard() is True:
            while 1:
                befehl=input(_("Are you sure to remove all files from media card? (y/n) "))
                if befehl == "y":
                    self.format_sd()
                    break
                elif befehl == "n":
                    break
                else:
                    print(_("Invalid input. Try again..."))

    def format_sd(self):
        print(_("Delete files in %s...") % self.cardpath)
        os.chdir(self.cardpath)
        for f in os.listdir():
            if os.path.isfile(f) is True:
                try:
                    os.remove(f)
                    self.show_message(_("%s deleted.") % f)
                except:
                    self.show_message(_("Failed to delete file. Check permissions."))
                    raise
            elif os.path.isdir(f) is True:
                try:
                    shutil.rmtree(f)
                    self.show_message(_("%s deleted.") % f)
                except:
                    self.show_message(_("Failed to delete directory. Check permissions."))
                    raise
        self.workdir(self.stdir)

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
        (d)elete all files on external memory card

        ------- create ------
        timelapse from (v)ideo
        timelapse from (i)mages
        (k)denlive project 

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
            elif befehl == 'd':
                self.confirm_format()
            elif befehl == 'v':
                ctl.countvid()
            elif befehl == 'i':
                ctl.countimg()
            elif befehl == 'k':
                kds.countvid()
            elif befehl == 'q':
                break
            else:
                print(_("Invalid input. Try again..."))

class KdenliveSupport:

    def __init__(self):
        
        self.wdir= os.getcwd()

    def create_project(self,folder):

        #load Kdenlive template without clips for later project file generation
        with open(os.path.join(cli.install_dir,"herostuff","kdenlive-template.xml"),"r") as f:
            self.tree = etree.parse(f)
        self.root = self.tree.getroot()
        self.mainbin = self.tree.find("playlist") #returns first match

        #use default profile from kdenlive config
        #avoid UnicodeDecodeError when reading file by using codecs package
        with codecs.open(os.path.join(os.path.expanduser('~'),".config","kdenliverc"),"r",encoding="utf-8",errors="ignore") as f:
            for line in f.readlines():
                if "default_profile" in line:
                    kdenlive_profile = line[16:-1]
                    cli.show_message(_("Found default profile: %s") % kdenlive_profile)
                    break

        profile = etree.SubElement(self.mainbin,"property")
        profile.set("name","kdenlive:docproperties.profile")
        profile.text = kdenlive_profile

        os.chdir(folder)

        #remove old kdenlive project file if existing
        try:
            os.remove("mlt-playlist.kdenlive")
            cli.show_message(_("Delete old Kdenlive project file."))
        except FileNotFoundError:
            cli.show_message(_("No existing Kdenlive project file to remove."))
           
        #add mediafiles
        counter = 1
        for f in sorted(glob.glob('*.MP4')):
        #for f in sorted(os.listdir()):
            newprod = etree.SubElement(self.root,"producer")
            newprod.set("id",str(counter))
            newprop = etree.SubElement(newprod,"property")
            newprop.text = os.path.join(folder,f)
            newprop.set("name","resource")
            #insert lines after root tag, otherwise kdenlive crashes at start
            self.root.insert(0,newprod)
            newentry = etree.SubElement(self.mainbin,"entry")
            newentry.set("producer",str(counter))
            counter +=1

        #save as new file
        self.tree.write("mlt-playlist.kdenlive")

        cli.show_message(_("Open Kdenlive project"))
        subprocess.run(["kdenlive","mlt-playlist.kdenlive"])
        
        cli.workdir(self.wdir)

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
            print("--> {0:^6} | {1:50} | {2:>}".format(_("no."),_("directory"),_("quantity")))
            for n in self.wherevid:
                print(_("--> {0:^6} | {1:50} | {2:>4}").format(n[0],n[1],n[2]))
            self.choosevid(counter)
        else:
            print(_("No video files found."))

    def choosevid(self,c):
        """Create and open Kdenlive project file for selected folder"""
        while 1:
            try:
                befehl = int(input(_("Select directory to create and open Kdenlive project (0 to cancel): ")))
                if befehl == 0:
                    break
                elif befehl > c or befehl < 0:
                    print(_("Invalid input, input must be integer between 1 and %d. Try again...") % c)
                else:
                    message = _("Processing Kdenlive project for %s") % self.wherevid[befehl-1][1]
                    cli.show_message(message)
                    self.create_project(self.wherevid[befehl-1][1])
                    break
            except ValueError:
                print(_("Invalid input (no integer). Try again..."))

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
            print("--> {0:^6} | {1:50} | {2:>}".format(_("no."),_("directory"),_("quantity")))
            for n in self.wherevid:
                print(_("--> {0:^6} | {1:50} | {2:>4}").format(n[0],n[1],n[2]))
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
                    print(_("Invalid input, input must be integer between 1 and %d. Try again...") % c)
                else:
                    message = _("Create timelapse for directory %s.") % self.wherevid[befehl-1][1]
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
            print("--> {0:^6} | {1:50} | {2:>}".format(_("no."),_("directory"),_("quantity")))
            for n in self.whereimg:
                print(_("--> {0:^6} | {1:50} | {2:>4}").format(n[0],n[1],n[2]))
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
                    print(_("Invalid input, input must be integer between 1 and %d. Try again...") % c)
                else:
                    print(_("Create timelapse for directory %s") % self.whereimg[befehl-1][1])
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


class TimelapseCalculator:
    
    def __init__(self):

        #data for dropdown menus saved in liststores
        resolution_data = [("5MPsilv","5 MP (2624x1968) - 3+Silver",1800000),
                            ("7MPsilv","7 MP (3072x2304) - 3+Silver",2300000),
                            ("10MPsilv","10 MP (3680x2760) - 3+Silver",3000000),
                            ("5MPsess","5 MP (2720x2040) - Session",2200000),
                            ("8MPsess","8 MP (3264x2448) - Session",2800000)
                            ]
        interval_data = [("2 photos per second",120),
                            ("1 photo per second",60),
                            ("2 seconds interval",30),
                            ("5 seconds interval",12),
                            ("10 seconds interval",6),
                            ("30 seconds interval",2),
                            ("60 seconds interval",1),
                            ]
        
        #create liststore rows
        for d in resolution_data:
            app.builder.get_object("list_res").append([d[0],d[1],d[2]])

        for d in interval_data:
            app.builder.get_object("list_intvl").append([d[0],d[1]])

        #set first entry as value
        app.builder.get_object("combobox_res").set_active(0)
        app.builder.get_object("combobox_intvl").set_active(0)

        self.filenum_label = app.builder.get_object("filenum_label")
        self.memory_label = app.builder.get_object("memory_label")
        self.tl_dur_label = app.builder.get_object("tl_dur_label")

        self.fsize = self.get_combobox_data(app.builder.get_object("combobox_res"),2)
        self.intvl = self.get_combobox_data(app.builder.get_object("combobox_intvl"),1)
        
        self.dur_hours = self.get_spinbutton_data(app.builder.get_object("spin_hours"))
        self.dur_min = self.get_spinbutton_data(app.builder.get_object("spin_minutes"))
        self.fps = self.get_spinbutton_data(app.builder.get_object("spin_fps"))

        self.set_fileinfo()

        #connect signals
        app.builder.connect_signals(Handler())

    def get_combobox_data(self,widget,list_col):
        row = widget.get_active_iter()
        model = widget.get_model()
        return int(model[row][list_col])

    def get_spinbutton_data(self,widget):
        return int(widget.get_value())

    def set_fileinfo(self):
        files = (self.dur_hours * 60 + self.dur_min) * self.intvl
        size = files * self.fsize
        tl_dur = files // self.fps
        
        self.filenum_label.set_text(str(files))
        self.memory_label.set_text(app.sizeof_fmt(size))
        self.tl_dur_label.set_text("%d min %d s" % (tl_dur // 60,tl_dur % 60))

    def standalone(self):
        app.builder.get_object("tl_calc_win").show_all()

cli = GoProGo()
ctl = TimeLapse()
kds = KdenliveSupport()
app = GoProGUI()
tlc = TimelapseCalculator()
