# EwastBin Cable
Sotware to broadcast on my Home Lab Cable Network.

To use this you'll need a bit of specialized hardware, main an IPQAM to ATSC Modulator if you live in North America. In other parts of the world you will need a different modulator, but they do exist.

[![images/atsc_modulator.jpg]](https://www.soukacatv.com/ip-to-rf-modulator_p74.html)

This one is manufactured by Souka TV, and will allow you to create 4 "channels". It can be readily found on AliExpress for a few hundred dollars (~$400).

Bigger one's due exist that will give you more channels but it can get expensive fast.

## Background
This video from Clabretro: [Ultimate Homelab Cable Setup](https://www.youtube.com/watch?v=W7m7OW2xrJE), inspired this project.

His set up only really supported a couple of chanels, and NTSC video.

I thought well that's silly I want HD tv in my home. After some digging I found what I needed readily available on AliExpress.

The modulates the signal to ATSC which is the broadcast standard in North America for Over the Air DTV signals. Almost all modern TV's still include a demodulator for these broadcasts. (I've been using a brand new 2024 Samsung 4K OLED for testing, and it's worked great perfectly).

With a bit more equipment I could also include regular broadcast DTV stations, or HDMI inputs.

## Warnings
I would be remiss to also to not include the following note:

__This is not intended to be hooked up to an antenna and broadcast over the airwaves. Doing so could land you in big trouble with your local goverment.__

## Network Diagram
+----------------------------+                                                                  
|                            |                                                                  
|                            |                                                                  
|            NAS             |                                                                  
|                            |                                                                  
|                            |                                                                  
+-------------+--------------+                                                                  
              |
              | 10GB
              | DAC
              |
              V
+----------------------------+                                                                  
|                            |                                                                  
|                            |                                                                  
|            LAN             +-----------------------------                                   
|                            |                            |                                     
|                            |                            |                                     
+-------------+--------------+                            |
              |                                           | Ethernet                                    
              | 10GB                                      |   NMS
              | DAC                                       |                                     
              |                                           |                                      
              v                                           |                                      
 +---------------------------+              +-------------+------------+                        
 |                           |   Ethernet   |                          |                        
 |                           |   Crossover  |                          |        COAX                                    COAX                
 |     Broadcast Server      +------------->|         Modulator        +-----------------------> Cable Spliter -----------------------> TV'S
 |                           |              |                          |                        
 |                           |              |                          |                        
 +---------------------------+              +--------------------------+                        

## Modulator Configuration
Once you get your modulator you will need to make a few cofigurations:

### NMS Configuration
I would configure the NMS port to use DHCP. It most likely will have a static IP when you get it, using a crossover cable to turn on DHCP.

If you want a static IP I would configure this in your router.

### Modulation Parameters
![images/modulation_params.png]

This allows you to fine tune the RF parameters. Here you can change the broadcast frequencies and tweak a few settings.

The checkboxes at the bottom do the following:
* MGT - Enables the Master Guide Table, required for the following options.
* VCT - Enables Virtual Channel Table. This basically provides your channel lineup to the TV.
* STT - System Time Table. Provides accurate time information.

More Details can be found on [WikiPedia](https://en.wikipedia.org/wiki/Program_and_System_Information_Protocol)

### Input Configuration
![images/main_ip_config.png]

Set a Static IP address for your main ethernet port. 

### SRC IP Config
![images/src_ip_config.png]

To create the channel sources you need to create a Unicast address with a port number.

### Source Configuration
![images/source_config.png]

This maps the SRC IP ports to RF broadcast channels. Simply configure each to broadcast to a different RF channel, and click forward to start broadcasting.

 ## Software Usage
 `$ python3 broadcaster.py -h`
 ```
 usage: broadcaster.py [-h] --broadcast_addr BROADCAST_ADDR --broadcast_port BROADCAST_PORT [--service_name SERVICE_NAME]
 [--service_provider SERVICE_PROVIDER] --media_dir MEDIA_DIR [--randomized] [--include_subtitles] [--debug]

options:
  -h, --help            show this help message and exit
  --broadcast_addr BROADCAST_ADDR
                        IP address to broadcast to
  --broadcast_port BROADCAST_PORT
                        Port to broadcast to
  --service_name SERVICE_NAME
                        The Name of your Channel
  --service_provider SERVICE_PROVIDER
                        The cable provider
  --media_dir MEDIA_DIR
                        Media Directory
  --randomized          Randomize the files
  --include_subtitles   Include Subtitles. Note only use this if you are sure all files have subtitle tracks.
  --debug               Print FFMPEG commands
```

Give it a `BROADCAST_ADDR` (configured above) and `BROADCAST_PORT` (also configured above) and a list of `MEDIA_DIRS` to play files from and it will do the rest.

It will handle
* Scaling Video's down, preserving aspect ratios,
* Letter Boxing/Pillar Boxing (Black Bars)
* Transcoding from input file type to the required MPEG-TS stream
* Broadcasting it to the modulator.

The following file extensions are white listed:
* .m4v
* .mp4
* .mov
* .mkv (Probably the best to store media in.)
* .avi

## Unsupoorted
There are a handful of things currently unsupported, (Mostly because of FFMPEG):

* TV Guide Info - This is supported for decoding. But FFMPEG doesn't apparently have a way of adding the EIT (See MGT configuration above) data to the MPEG-TS
* Closed Captioning - Once again FFMPEG supports this for decoding but can not encode it into the MPEG-TS
