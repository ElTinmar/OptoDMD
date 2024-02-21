ZEROMQ_JAR = '/home/martin/.local/jeromq/jeromq-0.6.0.jar'
javaclasspath(ZEROMQ_JAR)
import org.zeromq.*

fake_image = randi([0,255],[512,512]);

context = ZContext();
publisher = context.createSocket(SocketType.PUSH);
publisher.bind('tcp://*:5560');
publisher.send(mat2str(fake_image), 0)