# pfynder

## Intro 

pfynder is a simple tool to find function, object, and method names, usually in a Jupyter notebook.

## Dependencies 

It so far relies on a Linux environment, calling `find` and `grep` behind-the-scenes
 and then presents it nicely on the screen.

## Usage

It supports basic usage for searching a package (here "matplotlib") for a string ("xlim"):

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

## Wishlist

Future development:
- search _all_ installed packages (also from other venvs)
- use pure python (e.g. `pkg-resources`)
- tab-completion (please help!)
