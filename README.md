<h1>Exoplanet Discovery</h1>

<h2>About the App</h2>
This app uses data from the NASA Exoplanet Archive to return data about specific exoplanets using a local dynamic database.

<h2>About the Data</h2>
The data comes from the NASA Exoplanet Archive, and can be accessed <a url="https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=PS">at this link</a>, with many ways to sort and filter the dataset. This app uses the JSON file with the parameter <code>default_flag=1</code>. The reason for this is because the database contains duplicate exoplanets with different values. For each set of duplicates, only one has the default_flag of 1. Thus, this app avoids duplicates and returns default values.<br>
The data has many headers and is sparsely populated. Some key headers include "pl_name" (name of the planet), "hostname" (name of exoplanet's system), and "disc_year" (year planet was discovered). As for quantitative data, siginifcant headers include "sy_snum" (number of stars in planet's system), "sy_pnum" (number of planets in planet's system), pl_orbper (planet's orbital period in days), pl_orbsmax (planet's semi-major axis in au, comparable to orbital radius), pl_masse (planet's mass relative to Earth's mass), and sy_dist (distance to system in parsecs).<br>
More complete documentation can be found <a url="https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html">at this link</a>.<br>
DOI: 10.26133/NEA12<br>

<h2>Included Files and Directories</h2>
<ul>
<li>Dockerfile: used to build the container for this software package</li>
<li>docker-compose.yml: used to facilitate running the containers</li> 
<li>Makefile: used to facilitate building, running, and removing containers</li>
<li>requirements.txt: list of dependencies required to run the containers</li>
<li>src/api.py: contains all the methods and functions needed for the user to retrieve data. This script utilizes a Flask server so that all commands can be accessed through URL routes.</li>
<li>src/worker.py: used to keep track of and fulfill all jobs posted via the API</li>
<li>src/jobs.py: used to initialize the database where exoplanet data is locally stored and track all user-posted jobs</li>
<li>test/test_api.py: integration tests for the api</li>
<li>data/: directory where data will be stored locally</li>
<li>.github/workflows/: directory where continuous integration tests are contained</li>
<li>kubernetes/: directory where Kubernetes deployment scripts are contained</li>
</ul>

<h2>Building and Running Containers</h2>
Since code is containerized, no installations are required - just a machine that is capable of running Docker containers. First, ensure Dockerfile, docker_compose.yml, requirements.txt, and the folders src and data are in the same directory. Then, run the command:<br>
<code>make all</code><br>
The container for the Flask apps has now been built, and any previous running containers have been removed. All three containers are now running in the background. you may check the status of the containers by running <code>docker ps</code>.

<h2>API Query Commands and Sample Output</h2>
There are multiple routes that may be run on this app.<br>
<code>curl -X POST localhost:5000/data</code><br>
Running this query before any others is highly recommended, as the data needs to be loaded before being able to run any meaningful analyses. This route loads the entire dataset into the user's local /data directory. Sample output:<br>
<code>Data load succeeded</code> if load successful<br>
<code>Data load failed</code> if load failed<br><br>

<code>curl localhost:5000/data</code><br>
This query returns the entire dataset onto the user's command line in JSON format. Be careful when calling this, as it typically returns a huge amount of data. Sample output:<br>
<pre>
[
  {
    "ast_flag": 0,
    "cb_flag": 0,
    "dec": 46.0051696,
    "decstr": "+46d00m18.61s",
    "default_flag": 1,
    "disc_facility": "Kepler",
    "disc_instrument": "Kepler CCD Array",
    "disc_locale": "Space",
    "disc_pubdate": "2012-05",
    "disc_refname": "<a refstr=LISSAUER_ET_AL__2012 href=https://ui.adsabs.harvard.edu/abs/2012ApJ...750..112L/abstract target=ref> Lissauer et al. 2012 </a>",
    "disc_telescope": "0.95 m Kepler Telescope",
    "disc_year": 2011,
    "discoverymethod": "Transit",
    "dkin_flag": 0,
  ...
}
...
]
</pre><br>

<code>curl -X DELETE localhost:5000/data</code><br>
This query deletes all data from the Redis database, and consequently removes the data from the user's local /data directory. Sample output:<br>
<code>Deletion succeeded</code> if load successful<br>
<code>Deletion failed</code> if load failed<br><br>

<code>curl localhost:5000/planets</code><br>
This query returns a list of all valid planet names. This is to facilitate finding the name of a specific gene planet whose information you may want to query. Sample output:<br>
<pre>
[
  "Kepler-81 c",
  "Kepler-82 c",
  "Kepler-712 c",
  "Kepler-247 d",
  "Kepler-184 c",
  "Kepler-210 b",
  "Kepler-248 b",
  "Kepler-83 d",
  "Kepler-1711 b",
  "Kepler-174 c",
  "Kepler-186 d",
  "Kepler-55 b",
  "Kepler-251 d",
  "Kepler-253 d",
  "Kepler-561 c",
  "Kepler-215 b",
  "Kepler-62 b",
  "Kepler-192 c",
  "Kepler-33 f"
]
</pre><br>

<code>curl localhost:5000/planets/[pl_name]</code><br>
This query returns the information of the specific planet with name [pl_name]. The planet name must be in quotes, and any spaces must be replaced with the character sequence <code>%20</code> (example: <code>"Kepler-33%20f"</code> instead of <code>"Kepler-33 f"</code>). Sample output:<br>
<pre>
{
  "ast_flag": 0,
  "cb_flag": 0,
  "dec": 46.0051696,
  "decstr": "+46d00m18.61s",
  "default_flag": 1,
  "disc_facility": "Kepler",
  "disc_instrument": "Kepler CCD Array",
  "disc_locale": "Space",
  "disc_pubdate": "2012-05",
  "disc_refname": "<a refstr=LISSAUER_ET_AL__2012 href=https://ui.adsabs.harvard.edu/abs/2012ApJ...750..112L/abstract target=ref> Lissauer et al. 2012 </a>",
  "disc_telescope": "0.95 m Kepler Telescope",
  "disc_year": 2011,
  "discoverymethod": "Transit",
  "dkin_flag": 0,
  ...
}
</pre><br>
Alternatively, if ID was not found:<br>
<pre>
{
    "Planet name not found": 0
}
</pre><br>

<code>curl localhost:5000/planets/number</code><br>
This query returns the number of planets in the database. Sample output:<br>
<code>There are 5885 exoplanets in the database.</code><br>

<code>curl localhost:5000/planets/facilities</code><br>
This query returns the number of exoplanets found per facility across the whole database. Sample output:<br>
<pre>
{
  "Acton Sky Portal Observatory": 2,
  "Anglo-Australian Telescope": 35,
  "Apache Point Observatory": 2,
  "Arecibo Observatory": 3,
  "Atacama Large Millimeter Array (ALMA)": 1,
  ...
}
</pre><br>

<code>curl localhost:5000/planets/years</code><br>
This query returns the number of exoplanets found each year across the whole database. Sample output:<br>
<pre>
{
  "1992": 2,
  "1994": 1,
  "1995": 1,
  "1996": 6,
  "1997": 1,
  ...
}
</pre><br>

<code>curl localhost:5000/planets/methods</code><br>
This query returns the number of exoplanets found using each discovery method across the whole database. Sample output:<br>
<pre>
{
  "Astrometry": 5,
  "Disk Kinematics": 1,
  "Eclipse Timing Variations": 17,
  "Imaging": 83,
  "Microlensing": 237,
  ...
}
</pre><br>

<code>curl localhost:5000/planets/average_planets</code><br>
This query returns the average number of planets per planetary system in the database. Sample output:<br>
<code>The average number of planets per system is 1.34</code><br>

<code>curl localhost:5000/systems/average_stars</code><br>
This query returns the average number of stars per planetary system in the database. Sample output:<br>
<code>The average number of stars per system is 1.10</code><br>

<code>curl localhost:5000/jobs -X POST -d '{"pl_name": [planet name]}' -H "Content-Type: application/json"</code>
This query allows the user to submit a new job to the task queue, and it returns a confirmation of the received job. This will generate a diagram of the planetary system, showing the approximate star and planet sizes, star temperatures, and orbital radii, that can be downloaded later. [planet name] must correspond to the name of a planet in the database, or else it will revert to a default. Sample input and output:<br>
<pre>
curl localhost:5000/jobs -X POST -d '{"pl_name": "Kepler-592 b"}' -H "Content-Type: application/json"
</pre><br>
<pre>
{
  "id": "00be9f8c-1333-4642-9d18-889d13020996",
  "planet": "Kepler-592 b",
  "status": "submitted"
}
</pre><br>
Alternatively, if data packet invalid:<br>
<pre>
<!doctype html>
<html lang=en>
<title>400 Bad Request</title>
<h1>Bad Request</h1>
<p>Failed to decode JSON object: Expecting value: line 1 column 1 (char 0)</p>
</pre><br>

<code>curl localhost:5000/jobs</code>
This query lists all IDs for jobs submitted by the user for easy access. Sample output:<br>
<pre>
[
  "00be9f8c-1333-4642-9d18-889d13020996",
  "e7345cb2-a704-4b30-8f06-3ba2d58160c4",
  "74d58855-a2ec-4eb7-83d9-93d67d3a5db0"
]
</pre><br>

<code>curl localhost:5000/jobs/[job_id]</code>
This query lists status and information for a job, given its ID [job_id]. Sample output:<br>
<pre>
{
  "id": "00be9f8c-1333-4642-9d18-889d13020996",
  "planet": "Kepler-592 b",
  "status": "complete"
}
</pre><br>

<code>curl localhost:5000/download/[job_id] --output [output].png</code>
This query downloads the results of a previously requested job, given its ID [job_id]. The image will be downloaded as [output].png and saved in the working directory, where it can be copied to the user's local machine and viewed with an image viewer. This generates a diagram of the planetary system, showing the approximate star and planet sizes, star temperatures, and orbital radii. Sample input and output:<br>
<pre>
curl localhost:5000/download/00be9f8c-1333-4642-9d18-889d13020996 --output output.png
</pre><br>
<pre>
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 14929  100 14929    0     0  4189k      0 --:--:-- --:--:-- --:--:-- 4859k
</pre><br>
A <code>ls</code> command should show output.png among the listed files.<br>

<code>curl localhost:5000/help</code>
This query shows help and documentation for the different routes.<br>

<code>curl localhost:5000/debug</code>
A simple curl command used to ensure the Flask app is up and running. Sample output:<br>
<code>Hello, world!</code><br><br>

<h2>Logging and Unit Testing</h2>
This program includes docstrings and logs. Logs for a certain container may be accessed with <code>docker logs [container_ID]</code>, where [container_ID] may be found from the command <code>docker ps</code>.<br>
To run unit tests, navigate inside a container with the command <code>docker exec -it [container_id] /bin/bash</code> and then navigate to the source directory using <code>cd src</code>. The command <code>pytest</code> may be used to automatically run all unit and integration tests. There should be 10 tests that pass.<br>

<h2>Exiting Container</h2>
After all the desired scripts have been run, use the following commands to stop and remove the containers:<br>
<code>docker compose down</code><br>

<h2>Software Diagram</h2>
<img src="https://github.com/bethanygrimm/coe332/blob/58f7a468484522b68a305aa6f565a25fef925214/homework08/COE332%20HW%2008%20Diagram.drawio.png" alt="Software Diagram">
Software diagram for this application. This application is containerized with Docker. The user can access the Flask routes with curl commands, and output is given to the user on the terminal. Additionally, the Redis container persistently backs up data to the user's machine, since the path /data is mounted to the container. The containers - Redis, Flask, and the worker - are each mounted to a different port. Redis houses the databases for raw data, job metadata, job queue, and job results. The Flask container relies on the Redis container to retrieve exoplanet data, and is able to load and delete exoplanet data. The worker container relies on the Redis container to retrieve job information, and it updates job status and results when finished.
<br>

<h2>Citations</h2>
Data retrieved from NASA Exoplanet Archive. DOI: 10.26133/NEA12
