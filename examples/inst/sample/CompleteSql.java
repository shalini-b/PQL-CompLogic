package sample;

public class CompleteSql {
	private static DummySql scs = new DummySql();
	public static void main (String[] args) {
		UserControlledType a = new UserControlledType (false);
		UserControlledType b = new UserControlledType (true);
		
		scs.use ("SELECT * FROM logins WHERE name='"+"application"+
			 "' AND password = '"+"password"+"'");
		scs.use ("SELECT * FROM logins WHERE name='"+a.get("name") +
			 "' AND password = '"+a.get("password")+"'");
		System.out.println ("User-controlled attack");
		scs.use ("SELECT * FROM logins WHERE name='"+b.get("name") +
			 "' AND password = '"+b.get("password")+"'");
	}
}

