classdef frameDoneIPC < handle

    properties
        hSI
        listeners={}
        context
        publisher
        channel
        flags
    end 


    methods

        function obj = frameDoneIPC(zeromq_jar_path, zeromq_address, channel)

            % Pull in ScanImage API handle
            scanimageObjectName='hSI';
            W = evalin('base','whos');
            if ~ismember(scanimageObjectName,{W.name})
                fprintf('Can not find ScanImage API handle in base workspace. Please start ScanImage\n')
                obj.delete
                return
            end

            obj.hSI = evalin('base',scanimageObjectName); % get hSI from the base workspace

            % Add a listener to the the notifier that fires when a frame is acquired. 
            % This is the same notifier used for user functions.
            obj.listeners{1} = addlistener(obj.hSI.hUserFunctions ,'frameAcquired', @obj.fAcq);

            % initalize zeromq for IPC: send images to other processes
            javaclasspath(zeromq_jar_path)
            import org.zeromq.*
            obj.context = ZContext();
            obj.publisher = obj.context.createSocket(SocketType.PUSH);
            obj.publisher.bind(zeromq_address);
            
            obj.flags = ZMQ.DONTWAIT;
            obj.channel = channel;

        end 


        function delete(obj)

            cellfun(@delete,obj.listeners)

        end 

        function fAcq(obj,source,event,varargin)

            % get data structure
            dataBuffer = obj.hSI.hDisplay.stripeDataBuffer{obj.hSI.hDisplay.stripeDataBufferPointer};

            % get image data
            frame = dataBuffer.roiData{1}.imageData{obj.channel}{1};

            % rescale image
            im_min = obj.hSI.hChannels.channelLUT{obj.channel}(1);
            im_max = obj.hSI.hChannels.channelLUT{obj.channel}(2);
            frame = (single(frame) - single(im_min))./(single(im_max)-single(im_min));

            % send image via ZMQ 
            obj.publisher.send(serialize(frame'), obj.flags); 

        end 

    end 

end 