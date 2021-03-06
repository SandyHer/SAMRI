# -*- coding: utf-8 -*-

from __future__ import print_function, division, unicode_literals, absolute_import

import os

STIM_PROTOCOL_DICTIONARY={
	"EPI_BOLD_chr_longSOA":"chr_longSOA",
	"EPI_BOLD_jb_long":"jb_long",
	"EPI_CBV_alej":"alej",
	"EPI_CBV_chr_longSOA":"chr_longSOA",
	"EPI_CBV_chr_vlongSOA":"chr_vlongSOA",
	"EPI_CBV_jb_long":"jb_long",
	"EPI_CBV_jin6":"jin6",
	"EPI_CBV_jin10":"jin10",
	"EPI_CBV_jin20":"jin20",
	"EPI_CBV_jin40":"jin40",
	"EPI_CBV_jin60":"jin60",
	"EPI_CBV_jp_phasic":"jp_phasic",
	}

def fslmaths_invert_values(img_path):
	"""Calculates the op_string required to make an fsl.ImageMaths() node invert an image"""
	op_string = "-sub {0} -sub {0}".format(img_path)
	return op_string

def iterfield_selector(iterfields, selector, action):
	"""Include or exclude entries from iterfields based on a selector dictionary

	Parameters
	----------

	iterfields : list
	A list of lists (or tuples) containing entries fromatted at (subject_id,session_id,trial_id)

	selector : dict
	A dictionary with any combination of "sessions", "subjects", "trials" as keys and corresponding identifiers as values.

	action : "exclude" or "include"
	Whether to exclude or include (and exclude all the other) matching entries from the output.
	"""
	name_map = {"subjects": 0, "sessions": 1, "trials":2}
	keep = []
	for ix, iterfield in enumerate(iterfields):
		for key in selector:
			selector[key] = [str(i) for i in selector[key]]
			if iterfield[name_map[key]] in selector[key]:
				keep.append(ix)
				break
	if action == "exclude":
		iterfields = [iterfields[i] for i in range(len(iterfields)) if i not in keep]
	elif action == "include":
		iterfields = [iterfields[i] for i in keep]
	return iterfields

def datasource_exclude(in_files, excludes, output="files"):
	"""Exclude file names from a list that match a BIDS-style specifications from a dictionary.

	Parameters
	----------

	in_files : list
	A list of flie names.

	excludes : dictionary
	A dictionary with keys which are "subjects", "sessions", or "scans", and values which are lists giving the subject, session, or scan identifier respectively.

	output : string
	Either "files" or "len". The former outputs the filtered file names, the latter the length of the resulting list.
	"""

	if not excludes:
		out_files = in_files
	else:
		exclude_criteria=[]
		for key in excludes:
			if key in "subjects":
				for i in excludes[key]:
					exclude_criteria.append("sub-"+str(i))
			if key in "sessions":
				for i in excludes[key]:
					exclude_criteria.append("ses-"+str(i))
			if key in "scans":
				for i in excludes[key]:
					exclude_criteria.append("trial-"+str(i))
		out_files = [in_file for in_file in in_files if not any(criterion in in_file for criterion in exclude_criteria)]
	if output == "files":
		return out_files
	elif output == "len":
		return len(out_files)


def ss_to_path(subject_session):
	"""Concatenate a (subject, session) or (subject, session, scan) tuple to a BIDS-style path"""
	subject = "sub-" + subject_session[0]
	session = "ses-" + subject_session[1]
	return "/".join([subject,session])

def sss_to_source(source_format, subject=False, session=False, scan=False, subject_session_scan=False, base_directory=False, groupby=False):
	import os

	if any(a is False for a in [subject,session,scan]):
		(subject,session,scan) = subject_session_scan

	if groupby == "session":
		source = source_format.format("*", session, "*")
	else:
		source = source_format.format(subject, session, scan)
	if base_directory:
		source = os.path.join(base_directory, source)
	return source

def sss_filename(subject_session, scan, scan_prefix="trial", suffix="", extension=".nii.gz"):
	"""Concatenate subject-condition and scan inputs to a BIDS-style filename

	Parameters
	----------

	subject_session : list
	Length-2 list of subject and session identifiers

	scan : string
	Scan identifier

	suffix : string, optional
	Measurement type suffix (commonly "bold" or "cbv")
	"""
	# we do not want to modify the subject_session iterator entry
	from copy import deepcopy
	subject_session = deepcopy(subject_session)

	subject_session[0] = "sub-" + subject_session[0]
	subject_session[1] = "ses-" + subject_session[1]
	if suffix:
		suffix = "_"+suffix
	if scan_prefix:
		scan = "".join([scan_prefix,"-",scan,suffix,extension])
	else:
		scan = "".join([scan,suffix,extension])
	subject_session.append(scan)
	return "_".join(subject_session)
