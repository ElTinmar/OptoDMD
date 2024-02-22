function out = serialize(in)

   out = permute(in, [2 1 3:ndims(in)]);
   out = string(out);

   dimsToCat = ndims(out);
   if iscolumn(out)
      dimsToCat = dimsToCat-1; 
   end

   for i = 1:dimsToCat
      out = "[" + join(out, ",", i) + "]"; 
   end
end
