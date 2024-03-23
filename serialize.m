function out = serialize(im_num, im_time, image)
   % serialize 2D array to string
   
   out = string(image);
   out = join(out, ",", 2);
   out = join(out, ";", 1);
   out = string(im_num) + '|' + string(im_time) + '|' + out;
end
