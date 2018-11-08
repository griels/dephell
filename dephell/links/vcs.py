import attr
import re


@attr.s()
class VCSLink:
    server = attr.ib()
    author = attr.ib()
    project = attr.ib()

    vcs = attr.ib(default='git')
    protocol = attr.ib(default='ssh')
    user = attr.ib(default=None)

    ext = attr.ib(default=None)
    rev = attr.ib(default=None)
    name = attr.ib(default=None)

    # Examples:
    # HTTPS:
    # * https://github.com/r1chardj0n3s/parse.git
    # * https://gitlab.com/inkscape/inkscape.git
    # * https://orsinium@bitbucket.org/mnpenner/merge-attrs
    # SSH:
    # * git@github.com:r1chardj0n3s/parse.git
    # * git@gitlab.com:inkscape/inkscape.git
    # * ssh://hg@bitbucket.org/mnpenner/merge-attrs
    rex = re.compile(
        r'^'
        r'(?:(?P<vcs>[a-z]+)\+)?'                   # VCS name (optional)
        r'(?:(?P<protocol>ssh|https|http)://)?'     # protocol (optional)
        r'(?:(?P<user>.+)@)?'                       # username for auth on server (optional)
        r'(?P<server>[^/]+)[:/]'                    # server name
        r'(?P<author>.+)/'                          # project author
        r'(?P<project>[^\s#]+?)'                    # project name
        r'(?P<ext>\.git)?'                          # extension (save only for link constructing)
        r'(?:@(?P<rev>.+))?'                        # revision (commit hash, tag, branch)
        r'(?:#egg=(?P<name>.+))?'                   # dependency name
        r'$',
    )
    rex_hash = re.compile(r'[a-fA-F0-9]{40}')

    @classmethod
    def parse(cls, link: str, vcs: str='git', rev=None, name=None):
        match = cls.rex.search(link)
        if not match:
            return
        parsed = match.groupdict()
        parsed = {k: v for k, v in parsed.items() if v is not None}

        # default values
        if 'vcs' not in parsed:
            parsed['vcs'] = vcs
        if 'name' not in parsed:
            parsed['name'] = parsed['project']
        # we preffer parsed name
        # because pipenv take autogenerated names to VCS based deps
        if 'name' not in parsed:
            parsed['name'] = name

        # owerrite values
        if rev:
            parsed['rev'] = rev

        return cls(**parsed)

    @property
    def commit(self):
        if not self.rev:
            return
        if self.rex_hash.fullmatch(self.rev):
            return self.rev

    @property
    def short(self) -> str:
        """construct short link suitable for pipenv and poetry
        """
        link = ''
        if self.protocol != 'ssh':
            link += self.protocol + '://'
        if self.user:
            link += self.user + '@'
        link += self.server
        link += ':' if self.protocol == 'ssh' else '/'
        link += self.author + '/' + self.project
        if self.ext:
            link += self.ext
        return link

    @property
    def long(self) -> str:
        """construct full link suitable for pip
        """
        link = self.vcs + '+' + self.link
        if self.rev:
            link += '@' + self.rev
        if self.name:
            link += '#egg=' + self.name
        return link

    def __str__(self):
        return self.long
