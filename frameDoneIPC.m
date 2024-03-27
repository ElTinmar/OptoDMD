
classdef frameDoneIPC

    properties
        hSI
        listeners={}
        context
        publisher
        channel
        flags
        future
    end 

    methods

        function obj = frameDoneIPC(zeromq_jar_path, zeromq_protocol, zeromq_host, zeromq_port, channel)
            % initalize zeromq for IPC: send images to other processes
            javaclasspath(zeromq_jar_path)
            import org.zeromq.*
            obj.context = ZContext();

            % Pull in ScanImage API handle
            scanimageObjectName='hSI';
            W = evalin('base','whos');
            if ~ismember(scanimageObjectName,{W.name})
                fprintf('Can not find ScanImage API handle in base workspace. Please start ScanImage\n')
                obj.delete
                return
            end

            obj.hSI = evalin('base',scanimageObjectName); % get hSI from the base workspace
            obj.channel = channel;
            obj.flags = ZMQ.DONTWAIT;

            publisher_address = zeromq_protocol + zeromq_host + ":" + string(zeromq_port);
            obj.publisher = obj.context.createSocket(SocketType.PUSH);
            obj.publisher.bind(publisher_address);
            
            % Add a listener to the the notifier that fires when a frame is acquired. 
            % This is the same notifier used for user functions.
            obj.listeners{1} = addlistener(obj.hSI.hUserFunctions ,'frameAcquired', @obj.fAcq);
            % looks like this makes a copy of the object?
        end 


        function delete(obj)
            cellfun(@delete,obj.listeners)
        end 

        function fAcq(obj,source,event,varargin)

            % get image data
            buffer = obj.hSI.hDisplay.stripeDataBuffer{1};
            frame = buffer.roiData{1}.imageData{obj.channel}{1};
            im_num = buffer.frameNumberAcq;
            im_time = buffer.frameTimestamp;

            % rescale image
            im_min = obj.hSI.hChannels.channelLUT{obj.channel}(1);
            im_max = obj.hSI.hChannels.channelLUT{obj.channel}(2);
            frame = (single(frame) - single(im_min))./(single(im_max)-single(im_min));

            % clip between 0 and 1
            frame(frame<0) = 0;
            frame(frame>1) = 1;
            
            % send image via ZMQ 
            obj.publisher.send(serialize(im_num, im_time, frame'), obj.flags); 

        end 

    end 

end 
