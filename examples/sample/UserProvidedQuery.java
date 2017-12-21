package sample;

public class UserProvidedQuery {
	private boolean attacker;

	public UserProvidedQuery (boolean attacker) {
		this.attacker = attacker;
	}

	public String get () {
		String r;
 		r = "SELECT * FROM DB";
		return r;
	}
}
			
