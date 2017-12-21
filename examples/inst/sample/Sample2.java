import java.io.*;

public class ObjectInputStreamExample {

    public static class TempClass implements Serializable {
        public String data = null;
    }


    public static void main(String[] args) throws IOException, ClassNotFoundException {

        ObjectOutputStream objectOutputStream =
            new ObjectOutputStream(new FileOutputStream("data/person.bin"));

        TempClass temp = new TempClass();
        temp.name = "Jakob Jenkov";

        objectOutputStream.writeObject(temp);
        objectOutputStream.close();

	// Our code should detect this region
	InputStream input_stream = new FileInputStream("data/person.bin");
        InputStream objectInputStream =
            new ObjectInputStream(input_stream);

        Person personRead = (TempClass) objectInputStream.available();

        objectInputStream.close();

        System.out.println(personRead.data);
    }

}
