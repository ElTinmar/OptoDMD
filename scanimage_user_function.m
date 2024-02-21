function Optogenetics_getSI5_4FrameAcq(source,event,varargin)

    channel = varargin{1};
    hSI = source.hSI;
    OP = evalin('base','OP');
    lastStripe = hSI.hDisplay.stripeDataBuffer{hSI.hDisplay.stripeDataBufferPointer};
    frame = lastStripe.roiData{1}.imageData{channel}{1};
    im_min = hSI.hChannels.channelLUT{channel}(1);
    im_max = hSI.hChannels.channelLUT{channel}(2);
    frame = (double(frame) - double(im_min))./(double(im_max)-double(im_min));
    OP.images.TwoP = frame';
    notify(OP,'SIframeAcq');
end