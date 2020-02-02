<?xml version="1.0" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- Output to text (csv) -->
  <xsl:output method="text"/>

  <!-- Root -->
  <xsl:template match="/">
    <xsl:text>#name: sitemap&#xa;#description: Wikidebats&#xa;</xsl:text>
    <xsl:apply-templates select="//div[@id='mw-content-text']//li/a" />
  </xsl:template>

  <!-- Links to debates -->
  <xsl:template match="a">
    <xsl:value-of select="@href" />
    <xsl:text>;</xsl:text>
    <xsl:value-of select="@title" />
    <xsl:text>;0</xsl:text>
    <xsl:text>&#xa;</xsl:text> <!-- newline -->
  </xsl:template>
  
</xsl:stylesheet>
