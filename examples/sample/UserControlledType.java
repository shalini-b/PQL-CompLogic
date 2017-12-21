package sample;

public class UserControlledType {
	private boolean attacker;

	public UserControlledType (boolean attacker) {
		this.attacker = attacker;
	}

	public String get (String key) {
		String r;
		if (key.equals("name")) {
			r = "dbadmin";
		} else if (attacker && key.equals("password")) {
			r = "whatever' OR '1' = '1";
		} else {
			r = "some string";
		}

		System.out.println ("USER PROVIDES \""+r+"\" FOR KEY \""+key+"\"");
		return r;
	}
}
			
