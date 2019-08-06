This site uses the word-finding api <a href="http://www.datamuse.com/api/">Datamuse</a> and the python
package <a href="https://github.com/margaret/python-datamuse">python-datamuse</a> to retrieve data for
English words. <a href="https://observablehq.com/">D3 Observable</a> is used to generate visualizations
illustrating this data. The site was built using django.

<p><strong>Visualizations:</strong></p>
        <ul>
            <li>
                Word Frequencies: A chart illustrating the frequency of each words in a Word Set. Here, frequency
                refers to how often a word appears per million words of English text (according to
                <a href="https://books.google.com/ngrams">Google Books Ngrams</a> via Datamuse).
            </li>
            <li>
                Word Frequencies Scatterplot: For all words in a Word Set, plots the frequency vs. the number of
                occurrences in the Word Set.
            </li>
            <li>
                Related Words: For a given word, displays its related words for one or more word relationship types
                on a radial dendrogram.
            </li>
        </ul>
             
 <strong>Word Relationships</strong> These are the types of relationships that can be used when asking Datamuse for words related to a 
 certain word, identified by the three-letter code used in the rel_[code] Datamuse parameter:
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
</div>
 
 <strong>Format of Datamuse results:</strong>
 
 Queries to Datamuse return json such as the following (the response for 
 http://api.datamuse.com/words?rel_jja=test&md=dpf&max=3):
 <pre>
 [
  {
    "word": "results",
    "score": 1001,
    "tags": [
      "n",
      "f:345.463352"
    ],
    "defs": [
      "n\tsomething that results",
      "n\tthe semantic role of the noun phrase whose referent exists only by virtue of the activity denoted by the verb in the clause",
      "n\ta statement that solves a problem or explains how to solve the problem",
      "n\ta phenomenon that follows and is caused by some previous phenomenon"
    ],
    "defHeadword": "result"
  },
  {
    "word": "tube",
    "score": 1000,
    "tags": [
      "n",
      "f:59.310244"
    ],
    "defs": [
      "n\tconduit consisting of a long hollow object (usually cylindrical) used to hold and conduct objects or liquids or gases",
      "n\telectronic device consisting of a system of electrodes arranged in an evacuated glass or metal envelope",
      "n\t(anatomy) any hollow cylindrical body structure",
      "n\ta hollow cylindrical shape",
      "n\telectric underground railway"
    ]
  },
  {
    "word": "scores",
    "score": 999,
    "tags": [
      "n",
      "f:43.123432"
    ],
    "defs": [
      "n\ta large number or amount"
    ]
  }
]
</pre>

Here, score is an arbitrary number indicating the popularity of the word in English text, or in queries involving word 
relationships, the strength of the relationship (higher numbers indicate more popular or relevant words).

The items in "tags" indicate either the parts of speech of the word (such as "n" for noun) or the word's frequency in 
English text according to Google Books Ngrams ("f:...").

<strong>Running the site locally</strong>

First you must install Python 3.7 and the database system PostgreSQL (version 11). After installing PostgreSQL, you will 
need to create a new database. Open pgAdminIII and create a new database with the name "datamuse_words" and user 
"postgres".

Then clone datamuse_viz:
<pre>
git clone git@github.com:joncros/DataMuse_Viz.git
cd datamuse_viz
<!--git checkout dev-->
</pre>

<strong>branch 'dev'</strong>

The version of the site on the branch "dev" is mostly up to date, but is missing specific configuration settings needed 
for running the site in production. To run this branch, run:
<pre>
git checkout dev
</pre>
Then to complete setting up PostgreSQL, open the datamuse-viz file settings.py and look for this section:
<pre>
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'datamuse_words',
        'USER': 'postgres',
        'PASSWORD': 'wxZPAHz89GSHY',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
</pre>
On the line 'PASSWORD': 'wxZPAHz89GSHY', replace 'wxZPAHz89GSHY' with the password you set when installing PostgreSQL 
on your system. (If you are on linux, PostgreSQL may be pre-installed on your system without a password, in which case 
you will need to set the password.)

<strong>branch 'master'</strong>

The version of the site on the master branch is configured to work on the Heroku platform. It also uses redis-queue to 
offload longer running tasks in a separate process. Redis-queue is not supported in Windows, so to run the master branch 
you would need to run it from linux (Ubuntu 18 is suggested, since this is the OS that Heroku uses) or from Windows 10 
WSL (Windows Subsystem for Linux).

To run the master branch, type
<pre>
git checkout master
</pre>
on the command line. Then create a new text file named .env and add the following lines to it:
<pre>
DATABASE_URL="postgres://postgres:password@localhost/datamuse_words"
DEBUG=True
LOCAL=True
LOGLEVEL=DEBUG
SECRET_KEY="secret"
</pre>
replacing "password" in the first line with the password you set when installing PostgreSQL. (If you are on linux, 
PostgreSQL may be pre-installed on your system without a password, in which case you will need to set the password.)
<!--todo describe optional line ADDITIONAL_HOST in .env?-->

Then install the packages listed in requirements-dev.txt (currently, only fakeredis) that are required to run unit 
tests.

Then, you need to install <a href="https://devcenter.heroku.com/articles/heroku-cli">Heroku CLI</a>.

<strong>The following additional setup steps apply to either branch:</strong>

The required python packages are listed in requirements-primary.txt. You can install these packages manually using pip; 
or you can install all of these packages along with their dependencies using requirements.txt. It is recommended to 
first create a virtual environment using virtualenvwrapper (linux or macOS) or virtualenvwrapper-win (Windows). After 
installing mkvirtualenv, type the following on the command line:
<pre>mkvirtualenv datamuse_viz_env</pre>

To install all dependencies at once, type:
<pre>pip3 install --requirement requirements.txt </pre>

To work in this environment from the command line, type
<pre>workon datamuse_viz_env</pre>
If you use an IDE such as PyCharm, you also will need to set the environment to datamuse_viz_env in the ide. 
Instructions to do this in PyCharm are found 
<a href="https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html">here</a>.

To run the unit tests, type
<pre>py manage.py test</pre>

If you are on the dev branch, to run the server on your local machine, type
<pre>py manage.py runserver</pre>
and then visit http://127.0.0.1:8000 in your web browser to view the site.

If you are on the master branch, type
<pre>heroku local</pre>
and then visit http://127.0.0.1:5000 in your web browser to view the site.

<!--todo section on running master from a virtual machine?-->