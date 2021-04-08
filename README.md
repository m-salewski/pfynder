# pfynder

pfynder is a simple tool to find function, Object, and method names, usually in a Jupyter notebook.

It so far relies on a Linux environment, calling `find` and `grep` behind-the-scenes
 and then presents it nicely on the screen.

It supports basic usage:

```python
>>> from pfynder import pfynd
>>> pfynd("matplotlib","xlim")
matplotlib
	axes:
		get_xlim
		set_xlim
	pyplot:
		xlim
	tests:
		lower_xlim
		upper_xlim
	projections:
		set_xlim
```
