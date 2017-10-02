<?xml version="1.0"?>
<!--
 Gramps - a GTK+/GNOME based genealogy program

 Copyright (C) 2011       Michiel D. Nauta

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


-->
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:g="http://gramps-project.org/xml/1.4.0/">

<!--
    Transform a Gramps XML file into "canonical form", that is strip the
    timestamps in the change attributes, and order all elements for which
    the id attribute is used. The idea is that "canonical Gramps XML" files
    can be compared with eachother with the help of ordinary diff tools.
-->

<xsl:output method="xml"/>

<xsl:param name="replace_handles"/>
<xsl:key name="primary_obj" match="g:person|g:family|g:event|g:placeobj|g:source|g:repository|g:object|g:note|g:tag" use="@handle"/>

<xsl:template match="*|@*|text()">
    <xsl:copy>
        <xsl:apply-templates select="*|@*|text()"/>
    </xsl:copy>
</xsl:template>

<xsl:template match="@change">
</xsl:template>

<xsl:template match="g:researcher">
    <xsl:copy/>
</xsl:template>

<xsl:template match="g:people|g:families|g:events|g:places|g:sources|g:repositories|g:objects|g:notes|g:tags">
    <xsl:copy>
        <xsl:apply-templates select="*">
            <xsl:sort select="@id"/>
        </xsl:apply-templates>
    </xsl:copy>
</xsl:template>

<xsl:template match="@handle">
    <xsl:choose>
        <xsl:when test="$replace_handles='ID'">
            <xsl:attribute name="handle">
                <xsl:value-of select="../@id"/>
            </xsl:attribute>
        </xsl:when>
        <xsl:when test="$replace_handles='strip'">
        </xsl:when>
        <xsl:otherwise>
            <xsl:copy/>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="@hlink">
    <xsl:choose>
        <xsl:when test="$replace_handles='ID'">
            <xsl:attribute name="hlink">
                <xsl:value-of select="key('primary_obj',.)/@id"/>
            </xsl:attribute>
        </xsl:when>
        <xsl:when test="$replace_handles='strip'">
        </xsl:when>
        <xsl:otherwise>
            <xsl:copy/>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

</xsl:stylesheet>
