<tool id="history_summary" name="HistorySummary" version="0.2">
    <description>generates a html for summarizing the current history contents along with renaming the output files</description>
    <xml name="stdio">
        <stdio>
            <exit_code range="1:" />
        </stdio>
    </xml>
    <command><![CDATA[
        #set global $provenance = []
        #set global $jobs_table = {}
        #set global $datasets_table = {}

        #import re
        #set global $gap = "    "
        #set global $prefix = $get_prefix($os.environ['PWD'] + '/' + $os.environ['GALAXY_CONFIG_FILE'])

        #def get_prefix(path)
            #set $p = re.compile('^\s*prefix\s*=\s*(\S+)')
            #set $file = open(path)
            #for $line in $file
                #set $m = $p.search($line)
                #if $m
                    #return $m.group(1)
                #end if
            #end for
            #return ''
        #end def

        #def print_Dataset($ds, $ident)
            echo "${ident}DS: '$ds.name' $ds.state $ds.deleted $ds.purged" $ds.get_file_name() >> $output;
        #end def

        #def enum_DatasetCollection($dsc, $jobs)
            #for $el in $dsc.elements
                #if $el.hda
                    $enum_HistoryDatasetAssociation($el.hda, $jobs)
                #elif $el.ldda
                    $enum_LibraryDatasetAssociation($el.ldda, $jobs)
                #elif $el.child_collection
                    $enum_DatasetCollection($el.child_collection, $jobs)
                #end if
            #end for
        #end def

        #def print_JobToDataAssociation($jda, $useName, $rules, $isOutput=False)
            #if $jda.dataset
                #set $buf = "<li>"
                #if $useName
                    #set $buf += $jda.name + ": "
                #end if
                #set $buf += "<a href='" + $prefix + "/datasets/" + $__app__.security.encode_id($jda.dataset.id) + "/display?preview=True'><font color=black>"
                #if $rules and $rules.has_key(str($jda.dataset.id))
                    #set $file = $rules[str($jda.dataset.id)]
                #else
                    #set $file = $jda.dataset.name
                #end if
                #if $isOutput and $save_zip
                    ln -s "$jda.dataset.get_file_name()" "$os.path.join($history.name, $file)";
                #end if
                echo "$buf$file</font></a></li>" >> $output;
            #end if
        #end def

        #def print_JobParameter($parameters, $ident)
            #for $par in $parameters
                echo "${ident}P:$par.name '$par.value'" >> $output;
            #end for
        #end def

        #def job_state_color($job)
            #if $job.state == $job.states.OK
                #return "#B0F1B0"
            #elif $job.state == $job.states.RUNNING
                #return "#FFFFCC"
            #elif $job.state == $job.states.QUEUED
                #return "#FFFFCC"
            #elif $job.state == $job.states.WAITING
                #return "#EEE"
            #end if
            #return "#F9C7C5"
        #end def

        #def print_Job($job, $rules=None, $ident="")
            echo "<tr bgcolor='$job_state_color($job)'>" >> $output;
            echo "<td>$job.tool_id</td><td align=center>$job.exit_code</td>" >> $output;
            echo "<td>" >> $output;
            #for $jda in $job.input_datasets
                $print_JobToDataAssociation($jda, True, $rules)
            #end for
            echo "</td>" >> $output;
            echo "<td>" >> $output;
            #for $jda in $job.output_datasets
                $print_JobToDataAssociation($jda, False, $rules, True)
            #end for
            echo "</td>" >> $output;
            #*
            #for $jda in $job.input_dataset_collections
                $print_JobToDataAssociation($jda)
            #end for
            #for $jda in $job.output_dataset_collections
                $print_JobToDataAssociation($jda)
            #end for
            #for $jda in $job.input_library_datasets
                $print_JobToDataAssociation($jda)
            #end for
            #for $jda in $job.output_library_datasets
                $print_JobToDataAssociation($jda)
            #end for
            *#
        #end def

        #def enum_LibraryDatasetAssociation($hda, $jobs)
        #end def

        #def enum_HistoryDatasetAssociation($hda, $jobs)
            #if ($use_deleted or $hda.deleted == False) and ($use_hidden or $hda.visible == True)
                #set $original_hda = $hda
                #for $assoc in $original_hda.creating_job_associations
                    #set $jobs[$assoc.job.id] = $assoc.job
                #end for
            #end if
        #end def

        #def enum_HistoryDatasetCollectionAssociation($hdca, $jobs)
            #if ($use_deleted or $hdca.deleted == False) and ($use_hidden or $hdca.visible == True)
                #set $dsc = $hdca.collection
                $enum_DatasetCollection($dsc, $jobs)
            #end if
        #end def

        #def get_output_file($file, $jda)
            #if $jda.name
                #if $file != ""
                    #set $file += "."
                #end if
                #set $file += $jda.name
            #end if
            #if $jda.dataset.extension
                #if $file != ""
                    #set $file += "."
                #end if
                #set $file += $jda.dataset.extension
            #end if
            #return $file
        #end def

        #def rename_file($file, $rep)
            #for $k, $v in $rep.iteritems()
                #set $file = $file.replace($k, $v)
            #end for
            #return $file
        #end def

        #set global $history = $output.creating_job.history
        echo "<html>" > $output;
        echo "<head>" >> $output;
        echo "    <meta http-equiv='Content-Type' content='text/html; charset=utf-8' />" >> $output;
        echo "    <meta http-equiv='X-UA-Compatible' content='IE=Edge,chrome=1'>" >> $output;
        echo "    <style type='text/css'>" >> $output;
        echo "         .mytable, .mytable.td, .mytable.th { font-size:11pt; }" >> $output;
        echo "    </style>" >> $output;
        echo "</head>" >> $output;
        echo "<body>" >> $output;
        echo "<h1>$history.name</h1>" >> $output;

        #set $order = []
        #set $conf = {}
        #set $subst = {}
        #set $lines = $configuration.rstrip().split('\n')
        #if len($lines) > 1 or len($lines[0].rstrip()) > 0
            echo "<p>Parameters for rename<br>" >> $output;
            #for $line in $lines
                #set $arr = $line.split()
                echo "$arr<br>" >> $output;
                $order.append($arr[0])
                #set $subst[$arr[0]] = {}
                #if len($arr) == 1
                    #set $subst[$arr[0]]["PREFIX"] = ""
                    #set $conf[$arr[0]] = "PREFIX"
                #elif $arr[1].startswith("PREFIX=")
                    #set $z = $arr[1].split("=")
                    #set $subst[$arr[0]]["PREFIX"] = $z[1] if len($z) > 1 else ""
                    #set $conf[$arr[0]] = "PREFIX"
                #else
                    #set $conf[$arr[0]] = $arr[1].replace(".", "_0X")
                #end if
                #for $x in $arr[2:]
                    #set $y = $x.split("=")
                    #set $subst[$arr[0]][$y[0]] = $y[1] if len($y) > 1 else ""
                #end for
            #end for
        #end if

        #set $jobs = {}
        #for $hda in $history.datasets
            $enum_HistoryDatasetAssociation($hda, $jobs)
        #end for
        #for $hdca in $history.dataset_collections
            $enum_HistoryDatasetCollectionAssociation($hdca, $jobs)
        #end for

        #set $tools = {}
        #set $specified_jobs = set()
        #for $job_id, $job in $jobs.iteritems()
            #set $arr = $job.tool_id.split('/')
            #set $tar_tid = $arr[-1]
            #if $re.match(r'^[0-9\\.]+$', $arr[-1], $re.M)
                #set $tar_tid = $arr[-2]
            #end if
            #if not $tools.has_key($tar_tid)
                #set $tools[$tar_tid] = []
            #end if
            $tools[$tar_tid].append($job_id)
            #if $conf.has_key($tar_tid)
                $specified_jobs.add($job_id)
            #end if
        #end for

        #set $rules = {}
        #for $tar_tid in $order if len($order) > 0 else $tools.keys()
            #if $tools.has_key($tar_tid)
                ##echo ">$tar_tid $conf.get($tar_tid) $"|".join($subst[$tar_tid].keys())<br>" >> $output;
                #for $tar_jid in $tools[$tar_tid]
                    #for $jda in $jobs[$tar_jid].input_datasets
                        #set $tar_new = None
                        #if $jda.dataset
                            #if $conf.get($tar_tid) == "PREFIX"
                                #set $tar_new = $subst[$tar_tid][$conf.get($tar_tid)]
                            #elif str($jda.name) == $conf.get($tar_tid)
                                #if $rules.has_key(str($jda.dataset.id))
                                    #set $tar_new = $rules[str($jda.dataset.id)]
                                #else
                                    #set $tar_new = $jda.dataset.name
                                    #if $tar_new.endswith(":forward")
                                        #set $tar_new = $tar_new[:-8]
                                    #end if
                                    #if $tar_new.endswith(":forward")
                                        #set $tar_new = $tar_new[:-8]
                                    #end if
                                #end if
                            #end if
                            #if $tar_new != None
                                #break
                            #end if
                        #end if
                    #end for
                    #if $tar_new != None
                        #for $jda in $jobs[$tar_jid].output_datasets
                            #if $jda.dataset
                                #set $rules[str($jda.dataset.id)] = $rename_file($get_output_file($tar_new, $jda), $subst[$tar_tid])
                                ##echo "[$tar_new | $jda.dataset.id | $rules[str($jda.dataset.id)]]<br>" >> $output;
                            #end if
                        #end for
                    #end if
                #end for
            #end if
        #end for

        #if $save_zip
            mkdir "$history.name";
        #end if

        echo "<p><table border=1 cellpadding=2 bgcolor=#DFE5F9 style='mytable'>" >> $output;
        echo "<tr><th align=center>Tool</th><th align=center>EC</th><th align=center>Input</th><th align=center>Output</th>" >> $output;
        #for $job_id, $job in $jobs.iteritems()
            #if $job_id != $output.creating_job.id and (not $use_specified or $job_id in $specified_jobs)
                $print_Job($job, $rules)
            #end if
        #end for
        echo "</table>" >> $output;
        echo "</body>" >> $output;
        echo "</html>" >> $output;

        #if $save_zip
            rm $zip_file; zip -r $zip_file "$history.name";
        #end if
    ]]></command>
    <inputs>
        <param name="use_hidden" label='Include hidden contents' type="boolean" truevalue="True" falsevalue="" checked="True" />
        <param name="use_deleted" label='Include deleted contents' type="boolean" truevalue="True" falsevalue="" />
        <param name="use_specified" label='List only specified tools below' type="boolean" truevalue="True" falsevalue="" checked="True" />
        <param name="configuration" label='Specify tool, input parameter, and substitution rules to rename output files' type="text" area="True" />
        <param name="save_zip" label='Save all output files to a zip file' type="boolean" truevalue="True" falsevalue="" />
        <param name="dummy" label='Dummy input for workflows' type="data" />
    </inputs>
    <outputs>
        <data format="html" name="output"  label="${tool.name}: html"/>
        <data format="zip" name="zip_file" label="${tool.name}: zip">
            <filter>save_zip == True</filter>
        </data>
    </outputs>
    <help><![CDATA[

**Syntax of configuration** ::

  Column 1         - tool name
  Column 2         - input parameter name
  Column 3 or more - substitution rules in the format of match, match=, or match=replacement

**Example** ::

  tophat2 input1
  cufflinks input .accepted_hits.bam tabular=txt
  cuffquant samples.sample accepted_hits.bam.out_file=quan
  cuffnorm PREFIX=cuffnorm tabular=txt
  cuffdiff

- 'input1', 'input', and 'samples.sample' are used to rename output files of 'tophat2', 'cufflinks', and 'cuffquant', respectively.
- 'PREFIX' for cuffnorm generates the original output files with a specified prefix.
- For cuffdff, the original file names are used.
- From the output file names of cufflinks '.accepted_hits.bam' is removed and 'tabular' is replaced by 'txt'.
- From the output file names of cuffquant 'accepted_hits.bam.out_file' is replaced by 'quan'.

**Output**

+-------------------------------------+----+----------------------------------------------+---------------------------------------+
|                 Tool                | EC |                   Input                      |              Output                   |
+=====================================+====+==============================================+=======================================+
| toolshed.g2.bx.psu.edu/repos/       |  0 | - input1: hgrna1:forward                     | - hgrna1.align_summary.txt            |
| devteam/tophat2/tophat2/0.7         |    | - input2: hgrna1:reverse                     | - hgrna1.insertions.bed               |
|                                     |    | - gene_annotation_model: hg19dip.ensembl.gtf | - hgrna1.deletions.bed                |
|                                     |    |                                              | - hgrna1.junctions.bed                |
|                                     |    |                                              | - hgrna1.accepted_hits.bam            |
+-------------------------------------+----+----------------------------------------------+---------------------------------------+
| toolshed.g2.bx.psu.edu/repos/       |  1 | - input: hgrna1.accepted_hits.bam            | - hgrna1.genes_expression.txt         |
| devteam/cufflinks/cufflinks/2.2.1.0 |    | - reference_annotation_guide_file:           | - hgrna1.transcripts_expression.txt   |
|                                     |    |   hg19dip.ensembl.gtf                        | - hgrna1.assembled_isoforms.gtf       |
|                                     |    | - ref_file: hg19dip.fa                       | - hgrna1.total_map_mass.txt           |
|                                     |    | - global_model: hg19dip.ensembl.gtf          | - hgrna1.skipped.gtf                  |
+-------------------------------------+----+----------------------------------------------+---------------------------------------+
| toolshed.g2.bx.psu.edu/repos/       |  0 | - gtf_input: hg19dip.ensembl.gtf             | - hgrna1.quan.cxb                     |
| devteam/cuffquant/cuffquant/2.2.1.0 |    | - samples_0Xsample: hgrna1.accepted_hits.bam |                                       |
|                                     |    | - ref_file: hg19dip.fa                       |                                       |
+-------------------------------------+----+----------------------------------------------+---------------------------------------+
| toolshed.g2.bx.psu.edu/repos/       |  0 | - gtf_input: hg19dip.ensembl.gtf             | - cuffnorm.cds_fpkm_table.txt         |
| devteam/cuffquant/cuffnorm/2.2.1.0  |    | - conditionss_0Xsamples: hgrna1.quan.cxb     | - cuffnorm.cds_count_table.txt        |
|                                     |    | - conditionss_1Xsamples: hgrna2.quan.cxb     | - cuffnorm.tss_groups_fpkm_table.txt  |
|                                     |    |                                              | - cuffnorm.tss_groups_count_table.txt |
|                                     |    |                                              | - cuffnorm.genes_fpkm_table.txt       |
|                                     |    |                                              | - cuffnorm.genes_count_table.txt      |
|                                     |    |                                              | - cuffnorm.isoforms_fpkm_table.txt    |
|                                     |    |                                              | - cuffnorm.isoforms_count_table.txt   |
+-------------------------------------+----+----------------------------------------------+---------------------------------------+
| toolshed.g2.bx.psu.edu/repos/       |  0 | - gtf_input: hg19dip.ensembl.gtf             | - splicing_diff.tabular               |
| devteam/cuffquant/cuffdiff/2.2.1.2  |    | - conditionss_0Xsamples: hgrna1.quan.cxb     | - promoters_diff.tabular              |
|                                     |    | - conditionss_1Xsamples: hgrna2.quan.cxb     | - cds_diff.tabular                    |
|                                     |    | - ref_file: hg19dip.fa                       | - cds_exp_fpkm_tracking.tabular       |
|                                     |    |                                              | - cds_fpkm_tracking.tabular           |
|                                     |    |                                              | - cds_count_tracking.tabular          |
|                                     |    |                                              | - tss_groups_exp.tabular              |
|                                     |    |                                              | - tss_groups_fpkm_tracking.tabular    |
|                                     |    |                                              | - tss_groups_count_tracking.tabular   |
|                                     |    |                                              | - genes_exp.tabular                   |
|                                     |    |                                              | - genes_fpkm_tracking.tabular         |
|                                     |    |                                              | - genes_count_tracking.tabular        |
|                                     |    |                                              | - isoforms_exp.tabular                |
|                                     |    |                                              | - isoforms_fpkm_tracking.tabular      |
|                                     |    |                                              | - isoforms_count_tracking.tabular     |
|                                     |    |                                              | - output_cummerbund.sqlite            |
+-------------------------------------+----+----------------------------------------------+---------------------------------------+

    ]]></help>
</tool>
