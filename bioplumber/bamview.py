import rich
import subprocess
from collections import namedtuple
from textual.app import App
from textual.widgets import (Header,
                             Footer,
                             ListItem,
                             ListView,
                             TextArea,
                             Button,
                             DataTable,
                             Input,
                             DirectoryTree,
                             Static,
                             Collapsible,
                             Select,
                             MarkdownViewer,
                              TabbedContent,
                             Label)
from textual.screen import Screen
from textual.containers import Container,Horizontal,Vertical
from textual import on, work
from textual.binding import Binding
from textual.validation import Number

Contig= namedtuple('Contig', ['name', 'length'])

READ_STYLE={
    'A': '[white on green]A[/]',
    'C': '[white on blue]C[/]',
    'G': '[white on yellow]G[/]',
    'T': '[white on red]T[/]',
}
REFERENCE_STYLE={
    'A': '[bold white on green]A[/]',
    'C': '[bold white on blue]C[/]',
    'G': '[bold white on yellow]G[/]',
    'T': '[bold white on red]T[/]',
}

class Sequence:
    def __init__(self, seq: str, style: dict):
        self.seq = seq
        self.style = style
        self.styled_seq = self.style_sequence()

    def style_sequence(self):
        return ''.join(self.style.get(base, base) for base in self.seq)

class Alignment:
    def __init__(self, reference:str, bam:str, gene:str|None,engine:str='bash'):
        
        self.reference = reference
        self.bam = bam
        self.gene = gene
        self.engine = engine
        self.contigs_list= self.get_contigs_list()
    
    
    def get_contigs_list(self):
        if self.engine == 'bash':
            cmd = f"samtools idxstats {self.bam} | awk '{{print $1,$2}}'"
            output = [Contig(i.split()[0], int(i.split()[1])) for i in subprocess.check_output(cmd, shell=True).decode('utf-8').strip().split('\n')]

        elif self.engine == 'pysam':
            import pysam
            with pysam.AlignmentFile(self.bam, "rb") as bamfile:
                contigs = [Contig(contig, bamfile.get_reference_length(contig)) for contig in bamfile.references]
                output = contigs
        return output
        

class BamViewApp(App):
    def __init__(self, alignment: Alignment):
        super().__init__()
        self.alignment = alignment

    def compose(self):
        with Collapsible(collapsed=False, title="Contigs"):
            yield ListView(
            *[ListItem(
                    Label(f"{contig.name} ({contig.length})", classes="contig-item"),
                    id=f"contig-{index}",
                    classes="contig-list-item"
                ) for index,contig in enumerate(self.alignment.contigs_list)]
        )
aln= Alignment(reference="NA", bam="/Users/parsaghadermarzi/Desktop/ZWP421.bam", gene=None, engine='bash')
app= BamViewApp(alignment=aln)
app.run()