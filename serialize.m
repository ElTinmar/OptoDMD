function out = serialize(in)

   out = string(in');
   out = join(out, ",", 1);
   out = join(out, ";", 2);
end
