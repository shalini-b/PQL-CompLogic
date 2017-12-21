package sample;

public class Sample {
	private static DummySql scs = new DummySql();
	public static void main (String[] args) {
		RecursedControlledType g = new RecursedControlledType (true);
		String r = g.get("name");
		String t = g.get(r);	
		scs.use ("SELECT * FROM logins WHERE name='"+t +
			 "' AND password = '"+t+"'");
	}
}

