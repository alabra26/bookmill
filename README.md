# bookmill
A highly-opinionated Python framework for automating Jupyter Notebook creation from templated components.


## How bookmill works

Bookmill imagines a notebook as being composed of a series of interdependent Chapters that perform components of analysis. In the final product, these chapters work together to tell the story of the data. Before then, these chapters create a DAG that describes the conditional dependence of each Chapter on variables defined by previous Chapters. This allows the procedural generation of a notebook that follows each branch of analysis to its full conclusion, but stops if previous prerequisite results are not found. A representative example is described below.

### Piecewise notebook generation
Notebooks are generated piecewise through sequential addition of Chapters, blocks of cells that perform units of analysis. Chapters define their prerequisite variables, and add new variables to the notebook namespace upon successful execution. Chapters whose prerequisite variables do not exist in namespace are not added to the final notebook.

### Chapter architecture
Chapters consist of JSON objects that encode notebook cell components for sequential generation. These include:
- cell type (markdown, code)
- cell source (a multi-line string)
- cell tags (a list of strings)

### Chapter config storage
TODO

### Chapter dependency management
Code cell source is analyzed automatically to determine the variables that are required to execute that cell. Newly-defined variables are also determined in the same way. These two lists are aggregated on a per-chapter basis. Note that any external functions called that rely on global parameters or define new variables as a side-effect will break this behavior and are therefore prohibited by this package's structure. Refactor all such functions and methods to require parameters and return values.

### Example
Our example notebook visualizes the results of an EoY survey from our company's employees. The first Chapter is responsible for loading in the data.
```#code here```
If we can't load in the data, we can't generate any of the rest of the notebook, so we will stop at this point.
```#code here to demonstrate the assert statement to check the output```
```#code here to show the default cell injection in the fail case```
```#code here to show the success cell injection in the succeed case```
Once we've loaded the data, we hone in on a metric of interest. Let's take a look at manager effectiveness.
```#code displaying manager effectiveness```
Here we reach a significant branch point. If manager effectiveness is positive, we'll want to take a look at some outcomes that we expect from a successful manager, like meeting effectiveness and impact of contributions. If manager effectiveness is low, we wouldn't be interested in verifying positive results, but rather looking into possible repercussions of ineffective management, like skill development and work/life balance.
To do this, we conditionally define one new variable, indicating that manager effectiveness is either positive or negative.
```#code here conditionally defining positive_manager_effectiveness or negative_manager_effectiveness```
Now, we have two ensuing Chapters, one to visualize the aforementioned outcomes of successful management, and one to visualize repercussions of poor management.
```#code here that defines the Chapters```
Since the Chapters depend on one or the other of positive_manager_effectiveness or negative_manager_effectiveness, only the one that corresponds to our actual data will be appended to this notebook.

This example highlights several key features of this framework
##### 1) Failure/null case readouts
Baked into the framework is the notion that not all possible outputs are acceptable, and if a Chapter defines a variable to a value that does not meet spec, we inject different cells to display an error or "No results found" message.

##### 2) Variable splitting instead of preflight assertions

##### 3) Automated namespace management


# Installation

TODO

# Configuration


