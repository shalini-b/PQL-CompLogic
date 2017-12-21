package sample;

public class Sample {
	private static SystemCriticalSink scs = new SystemCriticalSink();
	public static void main (String[] args) {
		UserControlledType innocent = new UserControlledType (false);
		UserControlledType guilty = new UserControlledType (true);
		
		System.out.println ("Untainted use:");
		scs.use ("SELECT * FROM logins WHERE name='"+"application"+
			 "' AND password = '"+"password"+"'");

		System.out.println ();
		System.out.println ("User-controlled innocuous use:");
		scs.use ("SELECT * FROM logins WHERE name='"+innocent.get("name") +
			 "' AND password = '"+innocent.get("password")+"'");
		System.out.println ();
		System.out.println ("User-controlled attack");
		scs.use ("SELECT * FROM logins WHERE name='"+guilty.get("name") +
			 "' AND password = '"+guilty.get("password")+"'");
	}
}
