This site makes use of DataMuse to provide visualizations illustrating data about words and their relationships to other
 words. DataMuse is a RESTful API that provides access to data concerning words. More information can be found 
 <a href="http://www.datamuse.com/api/">here</a>. Currently (API version 1.1) only the English language is fully 
 supported by Datamuse; Spanish is partially supported (parameters for finding words related to the query word are not 
 supported). The site is built using Django and uses 
 <a href="https://github.com/margaret/python-datamuse">python-datamuse</a> to send queries to DataMuse. 
 
 <strong>Word Relationships</strong> These are the types of relationships that can be used when asking DataMuse for words related to a 
 certain word, identified by the three-letter code used in the rel_[code] DataMuse parameter:
 <div>
<table class="fullwidth">
<thead>
<th width=100>[code]</th>
<th>Description</th>
<th width=200>Example</th>
</thead>
<tbody>
<tr>
  <td align=left>jja</td>
  <td align=left>Popular Related Nouns (nouns that are frequently associated with the given word)</td>
  <td align=left>gradual &rarr; increase</td>
</tr>
<tr>
  <td align=left>jjb</td>
  <td align=left>Popular Related Adjectives (adjectives that are frequently associated with the given word)</td>
  <td align=left>beach &rarr; sandy</td>
</tr>
<tr>
  <td align=left>syn</td>
  <td align=left>Synonyms</td>
  <td align=left>ocean &rarr; sea</td>
</tr>
<tr>
  <td align=left>trg</td>
  <td align=left>"Triggers" (words that are statistically associated with the query word in the same piece of text.)</td>
  <td align=left>cow &rarr; milking</td>
</tr>
<tr>
  <td align=left>ant</td>
  <td align=left>Antonyms</td>
  <td align=left>late &rarr; early</td>
</tr>
<tr>
  <td align=left>spc</td>
  <td align=left>Direct Hypernyms (words with a similar, but broader meaning)</td>
  <td align=left>gondola &rarr; boat</td>
</tr>
<tr>
  <td align=left>gen</td>
  <td align=left>Direct Hyponyms (words with a similar, but more specific meaning)</td>
  <td align=left>boat &rarr; gondola</td>
</tr>
<tr>
  <td align=left>com</td>
  <td align=left>"Comprises" (things which this is composed of)</td>
  <td align=left>car &rarr; accelerator</td>
</tr>
<tr>
  <td align=left>par</td>
  <td align=left>"Part of" (things of which this is a part of)</td>
  <td align=left>trunk &rarr; tree</td>
</tr>
<tr>
  <td align=left>bga</td>
  <td align=left>Frequent followers (words that frequently follow this)</td>
  <td align=left>wreak &rarr; havoc</td>
</tr>
<tr>
  <td align=left>bgb</td>
  <td align=left>Frequent predecessors (words that frequently precede this)</td>
  <td align=left>havoc &rarr; wreak</td>
</tr>
<tr>
  <td align=left>rhy</td>
  <td align=left>Rhymes ("perfect" rhymes)</td>
  <td align=left>spade &rarr; aid</td>
</tr>
<tr>
  <td align=left>nry</td>
  <td align=left>Near rhymes (that is, approximate rhymes)</td>
  <td align=left>forest &rarr; chorus</td>
</tr>
<tr>
  <td align=left>hom</td>
  <td align=left>Homophones (sound-alike words)</td>
  <td align=left>course &rarr; coarse</td>
</tr>
<tr>
  <td align=left>cns</td>
  <td align=left>Consonant matches</td>
  <td align=left>sample &rarr; simple</td>
</tr>
</tbody>
</table>

 
 Planned visualizations:
 <ul>
 <li><strong>Word Frequency:</strong> Bubble chart [right term?} that shows a collection of words, with each word 
 surrounded by a circle whose size is proportional to how frequently the word occurs per million words of English text.
 [refer to google ngrams?]</li>
 <li><strong>Word Relationships:</strong> For a given query word, a [char type?] chart that shows words related to that 
 word in one of the ways outlined above, such as synonyms or frequent followers.</li>
 </ul>