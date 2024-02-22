% pathdef.m is admin only, workaround
restoredefaultpath; matlabrc

scanimage_folder='C:\Program Files\Vidrio\SI-Premium_2020.1.2_(2021-02-09)_bd806fcff6';
optoDMD_folder='P:\Code\OptoDMD-main';
zeromq_jar_path = 'P:\Code\OptoDMD-main\jeromq-0.6.0.jar';
zeromq_address = "tcp://*:5555";
channel = 1;

% add scanimage path
addpath(genpath(scanimage_folder));
addpath(genpath(optoDMD_folder));

% cd to optodmd
cd(optoDMD_folder)

% run scanimage
scanimage
ipc = frameDoneIPC(zeromq_jar_path, zeromq_address, channel)
