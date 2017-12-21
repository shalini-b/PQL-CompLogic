package sample;

import java.util.LinkedList;
import java.util.Iterator;

public class QuoteQuoter {
	private static class Range {
		public int start, end;
		public Range (int start, int end) {
			this.start = start;
			this.end = end;
		}
	}

	public static void safeUse (String[] i_unsafe, String[] f_a, 
				    SystemCriticalSink[] scs_a) {
		/* We know f and scs are the same in all results, so... */
		String f = f_a[0];
		SystemCriticalSink scs = scs_a[0];
		
		/* Find all ranges in f that match input strings. */

		LinkedList /*<Range>*/ l = new LinkedList();

		for (int i = 0; i < i_unsafe.length; i++) 
		{
			int s = f.indexOf (i_unsafe[i]);
			if (s != -1)
			{
				l.add (new Range (s, s+i_unsafe[i].length()));
			}
		}

		/* Build a new string, replacing ' with '' if we're
		 * inside any detected ranges. */

		StringBuffer result = new StringBuffer();
		for (int i = 0; i < f.length(); i++) {
			char c = f.charAt(i);
			if (c != '\'')
			{				
				result.append(c);
			} else {
				/* Is 'i' inside any range? */
				boolean quote = false;
				for (Iterator j = l.iterator(); j.hasNext(); ) {
					Range r = (Range)j.next();
					if ((i >= r.start) && (i < r.end))
					{
						quote = true;
						break;
					}
				}
				if (quote)
					result.append ("''");
				else
					result.append ("'");
			}
		}
		scs.use(result.toString());
	}
}
			
			
