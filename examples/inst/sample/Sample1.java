package sample;
import java.io.FileInputStream;
import java.io.InputStream;



public class Sample1 {
	public static void main (String[] args) {
	    execute();
	}

	public static void execute() {
	    try {
	      InputStream inpt;
	      System.out.println("InputStream file is not closes case : ");
	      inpt = new FileInputStream("/home/ubuntu/PQL-0.2/examples/sample/test.txt");
              
	      int i;
	      char c;
	      while ((i = inpt.read()) != -1){
		c = (char)i;
		System.out.print(c);
	      }
	      System.out.print("Finished test \n");
            }
	    catch(Exception e) {
	       System.out.println("Error running program");	
	    }
	}
}
