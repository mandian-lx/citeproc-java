%{?_javapackages_macros:%_javapackages_macros}

%define js_commit 2d1bb8dddf152f7c3e034dda3df3ec7e426939a3
%define js_shortcommit %(c=%{js_commit}; echo ${c:0:7})

Summary:	A Citation Style Language (CSL) processor for Java
Name:		citeproc-java
Version:	1.0.1
Release:	1
# Bundled code:
# citeproc-js			- Common Public Attribution License or AGPLv3+
# Name Parser			- ASL 2.0
# BibTeX to CSL converter	- ASL 2.0
# README contains further details.
License:	ASL 2.0 and (Common Public Attribution License or AGPLv3+)
Group:		Development/Java
URL:		https://michel-kraemer.github.io/citeproc-java/
Source0:	https://github.com/michel-kraemer/%{name}/archive/%{version}/%{name}-%{version}.tar.gz
Source1:	https://raw.githubusercontent.com/Juris-M/citeproc-js/%{js_shortcommit}/citeproc.js
Source2:	%{name}-1.0.1-org.eclipse.jface-metadata.xml
# Tests suite
#    citeprocZip
Source100:	https://github.com/Juris-M/citeproc-js/archive/2d1bb8dddf152f7c3e034dda3df3ec7e426939a3.zip
#    citeprocJs
Source101:	https://github.com/citation-style-language/test-suite/archive/9ec40dae08ba63422ea0ea18ac68d65d143a73cf.zip

Patch0:		%{name}-1.0.1-use_system_citationstyles_styles.patch
Patch1:		%{name}-1.0.1-use_system_citationstyles_locales.patch
Patch2:		%{name}-1.0.1-maven.patch
Patch3:		%{name}-1.0.1-osgi.patch
Patch4:		%{name}-1.0.1-encoding.patch

Patch99:	%{name}-1.0.1-eclipse.patch
Patch100:	%{name}-1.0.1-gradle-local-mode.patch

BuildArch:	noarch

BuildRequires:	jpackage-utils
BuildRequires:	java-headless
BuildRequires:	maven-local
BuildRequires:	gradle-local
BuildRequires:	j2v8
BuildRequires:	mvn(de.undercouch:underline-1.0.0)
BuildRequires:	mvn(org.antlr:antlr4)
BuildRequires:	mvn(org.antlr:antlr4-runtime)
BuildRequires:	mvn(org.apache.commons:commons-lang3)
BuildRequires:	mvn(org.mapdb:mapdb)
BuildRequires:	mvn(org.jbibtex:jbibtex)
BuildRequires:	mvn(jline:jline)
# The followings are required for tests only
BuildRequires:	mvn(com.carrotsearch:junit-benchmarks)
BuildRequires:	mvn(junit:junit)
BuildRequires:	mvn(com.fasterxml.jackson.core:jackson-databind)
BuildRequires:	mvn(org.fusesource.jansi:jansi)
BuildRequires:	mvn(org.apache.commons:commons-io)
BuildRequires:	mvn(org.eclipse.tycho:org.eclipse.jdt.core)
BuildRequires:	mvn(org.fusesource.jansi:jansi)
BuildRequires:	eclipse-platform
#BuildRequires:	mvn(org.mod4j.org.eclipse.jface:text)
#BuildRequires:	mvn(org.mod4j.org.eclipse.core:resources)
BuildRequires:	mvn(org.python:jython-standalone)
#BuildRequires:	mvn(org.citationstyles:styles)
#BuildRequires:	mvn(org.citationstyles:locales)


%description
A Citation Style Language (CSL) processor for Java.

The library interprets CSL styles and generates citations and bibliographies.
In addition to that, citeproc-java contains a BibTeX converter that is able
to map BibTeX database entries to CSL citations.

%files -f .mfiles
%doc README.md
%doc LICENSE.txt

#----------------------------------------------------------------------------

%package javadoc
Summary:	Javadoc for %{name}

%description javadoc
API documentation for %{name}.

%files javadoc -f .mfiles-javadoc
%doc LICENSE.txt

#----------------------------------------------------------------------------

%prep
%setup -q

# Delete prebuild JARs
find . -name "*.jar" -delete
find . -name "*.class" -delete

# Apply all patches
%patch0 -p1 -b .styles
%patch1 -p1 -b .locals
%patch2	-p1 -b .maven
#patch3 -p1 -b .osgi
%patch4 -p1 -b .utf8

%patch99 -p1 #	 -b .gradle
%patch100 -p1 -b .orig

# Add citeproc.js
mkdir -p ./citeproc-java/src-gen/main/resources/de/undercouch/citeproc/
cp -a %{SOURCE1} ./citeproc-java/src-gen/main/resources/de/undercouch/citeproc/

# Add test suite
#   Citeproc
mkdir -p citeproc-java/test-suite/extracted/
unzip -qq %{SOURCE101} -x '**/fixtures/local/*' -d citeproc-java/test-suite/extracted/
mv citeproc-java/test-suite/extracted/test-suite-9ec40dae08ba63422ea0ea18ac68d65d143a73cf/* citeproc-java/test-suite/extracted/
rm -fr citeproc-java/test-suite/extracted/test-suite-9ec40dae08ba63422ea0ea18ac68d65d143a73cf/
#   TestSuite
mkdir -p citeproc-java/test-suite/extracted/tests/fixtures/std
unzip -qq %{SOURCE100} -x '**/fixtures/local/*' -d citeproc-java/test-suite/extracted/tests/fixtures/std
mv citeproc-java/test-suite/extracted/tests/fixtures/std/citeproc-js-2d1bb8dddf152f7c3e034dda3df3ec7e426939a3/* citeproc-java/test-suite/extracted/tests/fixtures/std/
rm -fr citeproc-java/test-suite/test-suite/extracted/citeproc-js-2d1bb8dddf152f7c3e034dda3df3ec7e426939a3/

# fix deps
#   apache-commons-io
sed -i -e "s|org.apache.directory.studio:org.apache.commons.io:2.4|org.apache.commons:commons-io:2.4|" buildSrc/build.gradle
#   use system citationstyles-*
sed -i -e '/citationstyles/d' citeproc-java-tool/build.gradle
#   underline
sed -i -e "s|de.undercouch:underline:1.0.0|de.undercouch:underline-1.0.0:1.0.0|" citeproc-java-tool/build.gradle

#   metadata
sed -e 's|@LIBDIR@|%{_libdir}|g' %{SOURCE2} > maven-metadata.xml
%mvn_config resolverSettings/metadataRepositories/repository maven-metadata.xml

# fix encoding
find citeproc-java/src/main/java/de/undercouch/citeproc/script/ -name \*java -type f -exec sed -i -e 's|\xC2\xA0| |g' '{}' \;
sed -i -e 's|\xC3\xA8|e|g' -e 's|\xC3\xA9|e|g' citeproc-java/src/test/java/de/undercouch/citeproc/bibtex/BibTeXConverterTest.java

# Generate Maven metadata for gradle-dependency-management (required by XMvn connector)
sed -i "/publishedProjects =/s/.*/& project(':dependencyManagement'),/" build.gradle

%build
gradle build install -x test --offline
%mvn_artifact %{name}/build/poms/pom-default.xml %{name}/build/libs/%{name}-%{version}.jar

%install
%mvn_install -J %{name}/build/docs/javadoc

