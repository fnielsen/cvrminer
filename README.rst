CVR miner
=========

Data mining of CVR

Examples
--------

.. code:: python

  >>> from cvrminer.cvrfile import CvrFile
  >>> from cvrminer.virksomhed import Virksomhed
  >>> filename = '/home/fnielsen/data/cvr/cvr-permanent.json'  # or whatever
  >>> data = next(CvrFile(filename))
  >>> virksomhed = Virksomhed(data)
  >>> virksomhed.antal_ansatte
  0
  >>> cvr_file = CvrFile(filename)
  >>> cvr_file.write_virksomhed_feature_file()   # and wait
