ZEROMQ_JAR = '/home/martin/.local/jeromq/jeromq-0.6.0.jar'
javaclasspath(ZEROMQ_JAR)
import org.zeromq.*

% precompute a few random images (mat2str is a bit slow)
N_random = 10;
fake_image = {};
for i = 1:10
    fake_image{i} = mat2str(rand([512,512]), 3);
end

context = ZContext();
publisher = context.createSocket(SocketType.PUSH);
publisher.bind('tcp://*:5560');

for n = 1:100
    idx = mod(n,N_random) + 1;
    publisher.send(fake_image{idx}, 0);
end
