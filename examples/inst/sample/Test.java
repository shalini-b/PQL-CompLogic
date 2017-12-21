package sample;

public class Test {
	private static DummySql scs = new DummySql();
	public static void main (String[] args) {
		UserProvidedQuery control = new UserProvidedQuery (true);
		
		System.out.println ("Simple Non-recursive detection of SQL-Injection:");

		System.out.println ();
		scs.use (control.get());

	}
}
