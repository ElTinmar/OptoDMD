function out = serialize(in)
   % serialize 2D array to string
   
   out = string(in);
   out = join(out, ",", 2);
   out = join(out, ";", 1);
end
